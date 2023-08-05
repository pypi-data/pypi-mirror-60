# Copyright (C) 2018  Nexedi SA
#     Lukasz Nowak <luke@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.

try:
  import StringIO
except ImportError:
  from io import StringIO
import contextlib
import datetime
try:
  import httplib
except ImportError:
  from http import client as httplib
import ipaddress
import json
import mock
import multiprocessing
import os
import requests
import requests.exceptions
import shutil
import signal
import sys
import tempfile
import time
import unittest
import zc.lockfile
import socket

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

import caucase.cli
import caucase.http

from . import cli
from . import updater


def findFreeTCPPort(ip=''):
  """Find a free TCP port to listen to.
  """
  family = socket.AF_INET6 if ':' in ip else socket.AF_INET
  with contextlib.closing(socket.socket(family, socket.SOCK_STREAM)) as s:
    s.bind((ip, 0))
    return str(s.getsockname()[1])


@contextlib.contextmanager
def captured_output():
  new_out, new_err = StringIO.StringIO(), StringIO.StringIO()
  old_out, old_err = sys.stdout, sys.stderr
  try:
    sys.stdout, sys.stderr = new_out, new_err
    yield sys.stdout, sys.stderr
  finally:
    sys.stdout, sys.stderr = old_out, old_err


class KedifaMixin(object):
  def setUp(self):
    self.testdir = tempfile.mkdtemp()

    def cleanTestDir():
      shutil.rmtree(self.testdir)
    self.addCleanup(cleanTestDir)


class KedifaMixinCaucase(KedifaMixin):
  def createKey(self):
    key = rsa.generate_private_key(
      public_exponent=65537, key_size=2048, backend=default_backend())
    key_pem = key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.TraditionalOpenSSL,
      encryption_algorithm=serialization.NoEncryption()
    )
    return key, key_pem

  def generateCSR(self, ip):
    key_pem_file = os.path.join(self.testdir, '%s-key.pem' % (ip,))
    key, key_pem = self.createKey()
    csr_pem_file = os.path.join(self.testdir, '%s-csr.pem' % (ip,))

    with open(key_pem_file, 'w') as out:
      out.write(key_pem)

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
       x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"KeDiFa Test"),
    ])).add_extension(
      x509.SubjectAlternativeName([
        x509.IPAddress(ipaddress.ip_address(ip))
      ]),
      critical=False,
    ).sign(key, hashes.SHA256(), default_backend())

    with open(csr_pem_file, 'w') as out:
      out.write(csr.public_bytes(serialization.Encoding.PEM))

    return key_pem_file, csr_pem_file

  def generateKeyCertificateData(
    self,
    not_valid_before=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    not_valid_after=datetime.datetime.utcnow() + datetime.timedelta(days=2)):
    key, key_pem = self.createKey()
    subject = issuer = x509.Name([
      x509.NameAttribute(NameOID.COUNTRY_NAME, u"XX"),
      x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"YY"),
      x509.NameAttribute(NameOID.LOCALITY_NAME, u"Xx Yy"),
      x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Xyx Yxy"),
      x509.NameAttribute(NameOID.COMMON_NAME, u"xxx.yyy"),
    ])
    certificate = x509.CertificateBuilder().subject_name(
      subject
    ).issuer_name(
      issuer
    ).public_key(
      key.public_key()
    ).serial_number(
      x509.random_serial_number()
    ).not_valid_before(
      not_valid_before
    ).not_valid_after(
      not_valid_after
    ).sign(key, hashes.SHA256(), default_backend())
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)
    return key, key_pem, certificate, certificate_pem

  def createPem(self):
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData()
    self.pem = certificate_pem + key_pem

  def setUpCaucase(self):
    ip, port = os.environ['SLAPOS_TEST_IPV6'],\
       findFreeTCPPort(os.environ['SLAPOS_TEST_IPV6'])
    self.caucased = os.path.join(self.testdir, 'caucased')
    caucase_db = os.path.join(self.caucased, 'caucase.sqlite')
    self.caucase_service = os.path.join(self.testdir, 'service')
    os.mkdir(self.caucased)
    os.mkdir(self.caucase_service)
    self.caucase_runtime = multiprocessing.Process(
      target=caucase.http.main,
      kwargs=dict(
        argv=[
          '--db', caucase_db,
          '--server-key', os.path.join(self.caucased, 'server.key.pem'),
          '--netloc', '[%s]:%s' % (ip, port),
          '--service-auto-approve-count', '50'
        ]
      )
    )
    self.addCleanup(self.caucase_runtime.terminate)
    self.caucase_runtime.start()
    self.assertTrue(self.caucase_runtime.is_alive())
    self.caucase_url = 'http://[%s]:%s' % (ip, port)
    # give 5s for caucase to be available
    b = time.time()
    for i in range(50):
      try:
        requests.get(self.caucase_url)
      except BaseException:
        time.sleep(0.1)
      else:
        break
    else:
      self.fail(
        'Caucase not available after %.2fs seconds' % (time.time() - b))

  def setUpKey(self, common_name):
    # create key for the service and keep its downloaded ca_crt
    self.ca_crt_pem = os.path.join(self.caucase_service, 'ca-crt.pem')
    self.crl = os.path.join(self.caucase_service, 'crl.pem')
    user_ca_crt = os.path.join(self.caucase_service, 'user-ca-crt.pem')
    user_service_crl = os.path.join(self.caucase_service, 'user-crl.pem')
    cas = '--ca-url %(caucase_url)s --ca-crt %(ca_crt)s ' \
        '--crl %(service_crl)s --user-ca-crt %(user_ca_crt)s '\
        '--user-crl %(user_service_crl)s' % dict(
          caucase_url=self.caucase_url,
          ca_crt=self.ca_crt_pem,
          service_crl=self.crl,
          user_ca_crt=user_ca_crt,
          user_service_crl=user_service_crl,
        )
    self.cas = cas.split()

    kedifa_key_pem, csr_file = self.generateCSR(unicode(common_name))
    with captured_output() as (out, err):
      caucase.cli.main(argv=self.cas + [
        '--send-csr', csr_file
      ])

    self.assertEqual('', err.getvalue().strip())
    output = out.getvalue().strip()
    try:
      csr_id = output.split()[0]
    except IndexError:
      self.fail('csr_id parse failed: %s' % (output,))
    caucase.cli.main(argv=self.cas + [
       '--get-crt', csr_id, kedifa_key_pem
    ])

    return kedifa_key_pem

  def setUpKedifaKey(self, common_name):
    self.kedifa_key_pem = self.setUpKey(common_name)

  def setUpClientKey(self):
    self.client_key_pem = self.setUpKey(u'::5')

  def setUpKedifa(self, ip):
    self.db = os.path.join(self.testdir, 'pocket.sqlite')
    self.pidfile = os.path.join(self.testdir, 'kedifa.pid')
    self.logfile = os.path.join(self.testdir, 'kedifa.log')
    port = findFreeTCPPort(ip)
    self.kedifa_runtime = multiprocessing.Process(
      target=cli.http,
      args=(
        '--ip', ip,
        '--port', port,
        '--db', self.db,
        '--certificate', self.kedifa_key_pem,
        '--ca-certificate', self.ca_crt_pem,
        '--crl', self.crl,
        '--pidfile', self.pidfile,
        '--logfile', self.logfile)
    )
    self.kedifa_url = 'https://[%s]:%s/' % (ip, port)
    self.addCleanup(self.kedifa_runtime.terminate)
    self.kedifa_runtime.start()
    self.assertTrue(self.kedifa_runtime.is_alive())

    # give 5s for KeDiFa to be available
    b = time.time()
    for i in range(50):
      try:
        self.requests_get(self.kedifa_url + 'ping')
      except BaseException:
        time.sleep(0.1)
      else:
        break
    else:
      self.fail(
        'Kedifa not available after %.2fs seconds' % (time.time() - b))

    expected = 'Kedifa started at %s with pid %s stored in %s' % (
      self.kedifa_url, self.kedifa_runtime.pid, self.pidfile)
    self.assertAnyLogEntry(expected)
    self.assertLastLogEntry('"GET /ping HTTP/1.1" 401 0 "-" "python-requests')

  def reserveReference(self, *args, **kwargs):
    result = requests.post(
      self.kedifa_url + 'reserve-id',
      verify=self.ca_crt_pem, cert=self.client_key_pem)
    self.assertEqual(
      result.status_code,
      httplib.CREATED
    )
    location = result.headers.get('Location', '')
    self.assertRegexpMatches(
      location,
      r'^/[a-z0-9]{32}$'
    )
    reserved_reference = result.text
    self.assertRegexpMatches(
      reserved_reference,
      r'^[a-z0-9]{32}$'
    )

    self.assertEqual(
      '/' + reserved_reference,
      location
    )

    return reserved_reference

  def setUp(self):
    super(KedifaMixinCaucase, self).setUp()
    self.createPem()

    self.setUpCaucase()
    self.kedifa_ip = os.environ['SLAPOS_TEST_IPV6']
    self.setUpKedifaKey(self.kedifa_ip)
    self.setUpClientKey()
    self.setUpKedifa(self.kedifa_ip)
    self.reference = self.reserveReference()

  def requests_get(self, *args, **kwargs):
    return requests.get(verify=self.ca_crt_pem, *args, **kwargs)

  def requests_put(self, *args, **kwargs):
    return requests.put(verify=self.ca_crt_pem, *args, **kwargs)


class KedifaIntegrationTest(KedifaMixinCaucase, unittest.TestCase):
  def assertAnyLogEntry(self, entry):
    with open(self.logfile) as fh:
      log_line_list = fh.readlines()
    for log_line in log_line_list:
      if entry in log_line:
        return
    self.fail(
      'Entry %r not found in log:\n %s' % (entry, ''.join(log_line_list)))

  def assertLastLogEntry(self, entry):
    with open(self.logfile) as fh:
      last_log_line = fh.readlines()[-1]
    self.assertTrue(
      entry in last_log_line, '%r not found in %r' % (entry, last_log_line))

  def _getter_get(self, url, certificate, destination):
    cli.getter(
      url,
      '--out', destination,
      '--server-ca-certificate', self.ca_crt_pem,
      '--identity', certificate)

  def getter_get_raises(self, url, certificate):
    destination = tempfile.NamedTemporaryFile(dir=self.testdir).name
    with self.assertRaises(SystemExit) as assertRaisesContext:
      self._getter_get(url, certificate, destination)
    return destination, assertRaisesContext.exception.code

  def getter_get(self, url, certificate):
    destination = tempfile.NamedTemporaryFile(dir=self.testdir).name
    self._getter_get(url, certificate, destination)
    return destination

  def _updater_get(self, url, certificate, destination):
    mapping = tempfile.NamedTemporaryFile(dir=self.testdir, delete=False)
    mapping.write("%s %s" % (url, destination))
    mapping.close()
    state = tempfile.NamedTemporaryFile(dir=self.testdir, delete=False)
    state.close()
    cli.updater(
      '--once',
      '--server-ca-certificate', self.ca_crt_pem,
      '--identity', certificate,
      mapping.name,
      state.name
    )

  def updater_get(self, url, certificate):
    destination = tempfile.NamedTemporaryFile(dir=self.testdir).name
    self._updater_get(url, certificate, destination)
    return destination

  def test_reload_log(self):
    with open(self.pidfile) as pidfile:
      os.kill(int(pidfile.read()), signal.SIGHUP)

    # give some time for KeDiFa to react
    time.sleep(1)

    self.assertLastLogEntry('WARNING - KeDiFa reloaded.')

  def test_GET_root(self):
    result = self.requests_get(self.kedifa_url)
    # KeDiFa does not support nothing on / so for now it just raises
    # possibly in the future it will become self-describing interface
    self.assertEqual(
      httplib.BAD_REQUEST,
      result.status_code
    )
    self.assertEqual(
      'Wrong path',
      result.text
    )
    self.assertLastLogEntry('"GET / HTTP/1.1" 400')
    # check rotation support
    os.rename(self.logfile, self.logfile + '.rotated')
    result = self.requests_get(self.kedifa_url)
    self.assertEqual(
      httplib.BAD_REQUEST,
      result.status_code
    )
    self.assertLastLogEntry('"GET / HTTP/1.1" 400')

  def test_GET_not_existing(self):
    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)
    self.assertEqual(
      httplib.NOT_FOUND,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )
    self.assertLastLogEntry('"GET /%s HTTP/1.1" 404' % (self.reference,))

  def test_GET_existing(self):
    self.put()
    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      self.pem,
      result.text
    )
    self.assertLastLogEntry('"GET /%s HTTP/1.1" 200' % (self.reference,))

  def test_GET_unsigned_identity(self):
    self.put()

    _, key_pem, _, certificate_pem = self.generateKeyCertificateData()
    incorrect_key_pem = os.path.join(self.testdir, self.id())
    with open(incorrect_key_pem, 'w') as out:
      out.write(key_pem + certificate_pem)

    with self.assertRaises(requests.exceptions.SSLError):
      self.requests_get(
        self.kedifa_url + self.reference, cert=incorrect_key_pem)

  def revokeCaucaseServiceCertifice(self):
    with captured_output() as (out, err):
      caucase.cli.main(argv=self.cas + [
        '--revoke-crt', self.client_key_pem, self.client_key_pem
      ])

    self.assertEqual('', out.getvalue().strip())
    self.assertEqual('', err.getvalue().strip())

  def test_GET_revoked_identity(self):
    self.put()

    self.revokeCaucaseServiceCertifice()

    with open(self.pidfile) as pidfile:
      os.kill(int(pidfile.read()), signal.SIGHUP)

    # give some time for KeDiFa to react
    time.sleep(1)

    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)

    self.assertEqual(httplib.UNAUTHORIZED, result.status_code)
    self.assertEqual('transport', result.headers.get('WWW-Authenticate'))
    self.assertEqual('', result.text)

  @unittest.skip(
    'Hard to implement, and already being partially covered by '
    'test_GET_revoked_identity')
  def test_GET_expired_identity(self):
    raise NotImplementedError

  def test_GET_new_server_ca(self):
    self.put()
    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      self.pem,
      result.text
    )

    self.caucase_runtime.terminate()
    shutil.rmtree(self.caucased)
    shutil.rmtree(self.caucase_service)

    self.setUpCaucase()
    self.setUpKedifaKey(self.kedifa_ip)
    self.setUpClientKey()

    with open(self.pidfile) as pidfile:
      os.kill(int(pidfile.read()), signal.SIGHUP)

    # give some time for KeDiFa to react
    time.sleep(1)

    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      self.pem,
      result.text
    )

  def test_GET_existing_no_identity(self):
    self.put()
    result = self.requests_get(self.kedifa_url + self.reference)
    self.assertEqual(
      httplib.UNAUTHORIZED,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )
    self.assertEqual(
      'transport',
      result.headers['WWW-Authenticate']
    )

  def test_GET_existing_getter(self):
    self.put()
    result = self.getter_get(
      self.kedifa_url + self.reference, self.client_key_pem)
    with open(result) as result_file:
      self.assertEqual(
        self.pem,
        result_file.read()
      )

  def test_GET_getter_unsigned_identity(self):
    self.put()

    _, key_pem, _, certificate_pem = self.generateKeyCertificateData()
    incorrect_key_pem = os.path.join(self.testdir, self.id())
    with open(incorrect_key_pem, 'w') as out:
      out.write(key_pem + certificate_pem)

    result, code = self.getter_get_raises(
      self.kedifa_url + self.reference, incorrect_key_pem)

    self.assertFalse(os.path.isfile(result))
    self.assertEqual(1, code)

  def test_GET_existing_getter_name_does_not_match(self):
    self.put()

    result, code = self.getter_get_raises(
      self.kedifa_url + self.reference + 'MISSING', self.client_key_pem)

    self.assertFalse(os.path.isfile(result))
    self.assertEqual(1, code)

  def test_GET_existing_updater(self):
    self.put()
    result = self.updater_get(
      self.kedifa_url + self.reference, self.client_key_pem)
    with open(result) as result_file:
      self.assertEqual(
        self.pem,
        result_file.read()
      )

  def test_GET_updater_unsigned_identity(self):
    self.put()

    _, key_pem, _, certificate_pem = self.generateKeyCertificateData()
    incorrect_key_pem = os.path.join(self.testdir, self.id())
    with open(incorrect_key_pem, 'w') as out:
      out.write(key_pem + certificate_pem)

    result = self.updater_get(
      self.kedifa_url + self.reference, incorrect_key_pem)

    self.assertFalse(os.path.isfile(result))

  def test_GET_existing_updater_name_does_not_match(self):
    self.put()

    result = self.updater_get(
      self.kedifa_url + self.reference + 'MISSING', self.client_key_pem)

    self.assertFalse(os.path.isfile(result))

  def test_GET_existing_exact(self):
    self.put()
    result = self.requests_get(
      self.kedifa_url + self.reference + '/1', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      self.pem,
      result.text
    )

  def test_GET_list_empty(self):
    result = self.requests_get(
      self.kedifa_url + self.reference + '/list', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      {"key_list": []},
      result.json()
    )

  def test_GET_list(self):
    self.put()
    result = self.requests_get(
      self.kedifa_url + self.reference + '/list', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      {"key_list": ["1"]},
      result.json()
    )

  def test_GET_list_no_identity(self):
    self.put()
    result = self.requests_get(
      self.kedifa_url + self.reference + '/list')
    self.assertEqual(
      httplib.UNAUTHORIZED,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )
    self.assertEqual(
      'transport',
      result.headers['WWW-Authenticate']
    )

  def test_GET_order(self):
    _, new_key_pem, _, new_certificate_pem = self.generateKeyCertificateData(
      not_valid_before=datetime.datetime.utcnow() - datetime.timedelta(days=2),
    )
    _, old_key_pem, _, old_certificate_pem = self.generateKeyCertificateData(
      not_valid_before=datetime.datetime
      .utcnow() - datetime.timedelta(days=10),
    )
    auth = self.generateauth()

    self.put(self.reference, data=new_certificate_pem + new_key_pem, auth=auth)
    # wait for some time to pass, in order to submission_date to kick in
    time.sleep(0.1)
    self.put(self.reference, data=old_certificate_pem + old_key_pem, auth=auth)

    result = self.requests_get(
      self.kedifa_url + self.reference + '/list', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      {"key_list": ["2", "1"]},
      result.json()
    )

    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      old_certificate_pem + old_key_pem,
      result.text
    )

    result = self.requests_get(
      self.kedifa_url + self.reference + '/2', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      old_certificate_pem + old_key_pem,
      result.text
    )

    result = self.requests_get(
      self.kedifa_url + self.reference + '/1', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      new_certificate_pem + new_key_pem,
      result.text
    )

  def test_GET_invalid_yet(self):
    from app import SQLite3Storage
    pocket_db = SQLite3Storage(self.db)
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData()
    not_valid_before = datetime.datetime.utcnow() + datetime.timedelta(days=10)
    not_valid_after = datetime.datetime.utcnow() + datetime.timedelta(days=15)
    _, invalid_yet_key_pem, _, invalid_yet_certificate_pem = \
        self.generateKeyCertificateData(
          not_valid_before=not_valid_before,
          not_valid_after=not_valid_after
        )

    auth = self.generateauth()

    pocket_db.addCertificate(
      self.reference,
      datetime.datetime.now(),
      not_valid_before,
      not_valid_after,
      invalid_yet_key_pem + invalid_yet_certificate_pem
    )
    del pocket_db
    self.put(self.reference, data=certificate_pem + key_pem, auth=auth)

    result = self.requests_get(
      self.kedifa_url + self.reference + '/list', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      {"key_list": ["2"]},
      result.json()
    )

    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      certificate_pem + key_pem,
      result.text
    )

    result = self.requests_get(
      self.kedifa_url + self.reference + '/2', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      certificate_pem + key_pem,
      result.text
    )

    result = self.requests_get(
      self.kedifa_url + self.reference + '/1', cert=self.client_key_pem)
    self.assertEqual(
      httplib.NOT_FOUND,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )

  def test_GET_expired(self):
    from app import SQLite3Storage
    pocket_db = SQLite3Storage(self.db)
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData()
    not_valid_before = datetime.datetime.utcnow() - datetime.timedelta(days=10)
    not_valid_after = datetime.datetime.utcnow() - datetime.timedelta(days=5)
    _, expired_key_pem, _, expired_certificate_pem = \
        self.generateKeyCertificateData(
          not_valid_before=not_valid_before,
          not_valid_after=not_valid_after
        )

    auth = self.generateauth()

    pocket_db.addCertificate(
      self.reference,
      datetime.datetime.now(),
      not_valid_before,
      not_valid_after,
      expired_key_pem + expired_certificate_pem
    )
    del pocket_db
    self.put(self.reference, data=certificate_pem + key_pem, auth=auth)

    result = self.requests_get(
      self.kedifa_url + self.reference + '/list', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      {"key_list": ["2"]},
      result.json()
    )

    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      certificate_pem + key_pem,
      result.text
    )

    result = self.requests_get(
      self.kedifa_url + self.reference + '/2', cert=self.client_key_pem)
    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      certificate_pem + key_pem,
      result.text
    )

    result = self.requests_get(
      self.kedifa_url + self.reference + '/1', cert=self.client_key_pem)
    self.assertEqual(
      httplib.NOT_FOUND,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )

  def generateauth(self, reference=None):
    if reference is None:
      reference = self.reference
    result = self.requests_get(
      self.kedifa_url + reference + '/generateauth')
    self.assertEqual(
      httplib.CREATED,
      result.status_code
    )
    return result.text

  def test_GET_generateauth(self):
    auth = self.generateauth()

    self.assertRegexpMatches(
      auth,
      r'^[a-z0-9]{32}$'
    )

    result = self.requests_get(
      self.kedifa_url + self.reference + '/generateauth')
    self.assertEqual(
      httplib.FORBIDDEN,
      result.status_code
    )
    self.assertEqual('Already exists', result.text)

  def test_GET_generateauth_no_reserved(self):
    key = 'unreserved'
    result = self.requests_get(
      self.kedifa_url + key + '/generateauth')
    self.assertEqual(
      httplib.NOT_FOUND,
      result.status_code
    )
    self.assertEqual(
      'Reservation required',
      result.text
    )

  def put(self, key=None, data=None, auth=None):
    if key is None:
      key = self.reference
    if data is None:
      data = self.pem
    if auth is None:
      auth = self.generateauth()
    url = self.kedifa_url + key + '?auth=%s' % (auth, )
    result = self.requests_put(url, data=data, headers={
      'Content-Type': 'application/x-x509-ca-cert',
    })
    self.assertEqual(
      httplib.CREATED,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )
    self.assertRegexpMatches(
      result.headers.get('Location', ''),
      r'^/%s/\d+$' % key
    )
    self.assertLastLogEntry('"PUT /%s?auth=%s HTTP/1.1" 201' % (key, auth))

  def test_PUT(self):
    self.put()

  def test_PUT_multiple_same_reference(self):
    auth = self.generateauth()
    self.put(auth=auth)
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData(
      not_valid_before=datetime.datetime.utcnow() - datetime.timedelta(days=4),
      not_valid_after=datetime.datetime.utcnow() + datetime.timedelta(days=2)
    )
    self.put(data=key_pem + certificate_pem, auth=auth)

  def test_PUT_multiple_different_reference(self):
    # put first certificate
    self.put()

    # put another certificate on another reference
    reference = self.reserveReference()
    auth = self.generateauth(reference)
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData(
      not_valid_before=datetime.datetime.utcnow() - datetime.timedelta(days=4),
      not_valid_after=datetime.datetime.utcnow() + datetime.timedelta(days=2)
    )
    self.put(key=reference, data=key_pem + certificate_pem, auth=auth)

  def test_PUT_certificate_expired(self):
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData(
      not_valid_before=datetime.datetime.utcnow() - datetime.timedelta(days=4),
      not_valid_after=datetime.datetime.utcnow() - datetime.timedelta(days=2)
    )
    auth = self.generateauth()
    url = self.kedifa_url + self.reference + '?auth=%s' % (auth, )
    result = self.requests_put(url, data=key_pem + certificate_pem)
    self.assertEqual(
      httplib.UNPROCESSABLE_ENTITY,
      result.status_code
    )
    self.assertEqual(
      'Certificate expired',
      result.text
    )

  def test_PUT_certificate_not_valid_yet(self):
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData(
      not_valid_before=datetime.datetime.utcnow() + datetime.timedelta(days=2),
      not_valid_after=datetime.datetime.utcnow() + datetime.timedelta(days=4)
    )
    auth = self.generateauth()
    url = self.kedifa_url + self.reference + '?auth=%s' % (auth, )
    result = self.requests_put(url, data=key_pem + certificate_pem)
    self.assertEqual(
      httplib.UNPROCESSABLE_ENTITY,
      result.status_code
    )
    self.assertEqual(
      'Certificate not valid yet',
      result.text
    )

  def test_PUT_key_before_certificate(self):
    _, key_pem, _, certificate_pem = self.generateKeyCertificateData()
    auth = self.generateauth()
    url = self.kedifa_url + self.reference + '?auth=%s' % (auth, )
    result = self.requests_put(url, data=key_pem + certificate_pem)
    self.assertEqual(
      httplib.CREATED,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )

  def test_PUT_key_only(self):
    _, key_pem, _, _ = self.generateKeyCertificateData()
    auth = self.generateauth()
    url = self.kedifa_url + self.reference + '?auth=%s' % (auth, )
    result = self.requests_put(url, data=key_pem)
    self.assertEqual(
      httplib.UNPROCESSABLE_ENTITY,
      result.status_code
    )
    self.assertEqual(
      'Certificate incorrect',
      result.text
    )

  def test_PUT_certificate_only(self):
    _, _, _, certificate_pem = self.generateKeyCertificateData()
    auth = self.generateauth()
    url = self.kedifa_url + self.reference + '?auth=%s' % (auth, )
    result = self.requests_put(url, data=certificate_pem)
    self.assertEqual(
      httplib.UNPROCESSABLE_ENTITY,
      result.status_code
    )
    self.assertEqual(
      'Key incorrect',
      result.text
    )

  def test_PUT_certificate_key_mismatch(self):
    _, _, _, certificate_pem = self.generateKeyCertificateData()
    _, key_pem, _, _ = self.generateKeyCertificateData()
    auth = self.generateauth()
    url = self.kedifa_url + self.reference + '?auth=%s' % (auth, )
    result = self.requests_put(url, data=certificate_pem + key_pem)
    self.assertEqual(
      httplib.UNPROCESSABLE_ENTITY,
      result.status_code
    )
    self.assertEqual(
      'Key and certificate do not match',
      result.text
    )

  def test_PUT_bad(self):
    auth = self.generateauth()
    url = self.kedifa_url + self.reference + '?auth=%s' % (auth, )
    result = self.requests_put(url, data='badcert')
    self.assertEqual(
      httplib.UNPROCESSABLE_ENTITY,
      result.status_code
    )
    self.assertEqual(
      'Certificate incorrect',
      result.text
    )

  def test_PUT_no_auth(self):
    url = self.kedifa_url + self.reference
    result = self.requests_put(url, data=self.pem)
    self.assertEqual(
      httplib.BAD_REQUEST,
      result.status_code
    )
    self.assertEqual(
      'Missing auth',
      result.text
    )

  def test_PUT_bad_auth(self):
    url = self.kedifa_url + self.reference + '?auth=wrong'
    result = self.requests_put(url, data=self.pem)
    self.assertEqual(
      httplib.UNAUTHORIZED,
      result.status_code
    )
    self.assertEqual(
      '',
      result.text
    )
    self.assertEqual(
      'transport',
      result.headers['WWW-Authenticate']
    )

  def addExpiredNonvalidyetCertificate(self, key):
    from app import SQLite3Storage
    pocket_db = SQLite3Storage(self.db)

    not_valid_before_valid = datetime.datetime.utcnow() - \
        datetime.timedelta(days=2)
    not_valid_before_invalid = datetime.datetime.utcnow() + \
        datetime.timedelta(days=2)

    not_valid_after_valid = datetime.datetime.utcnow() + \
        datetime.timedelta(days=1)
    not_valid_after_invalid = datetime.datetime.utcnow() - \
        datetime.timedelta(days=1)

    pocket_db.addCertificate(
      key,
      datetime.datetime.now(),
      not_valid_before_valid,
      not_valid_after_invalid,
      'cert'
    )

    pocket_db.addCertificate(
      key,
      datetime.datetime.now(),
      not_valid_before_invalid,
      not_valid_after_valid,
      'cert'
    )

  def _getDBCertificateCount(self):
    from app import SQLite3Storage
    pocket_db = SQLite3Storage(self.db)
    return pocket_db._executeSingleRow(
      'SELECT COUNT(*) FROM certificate')['COUNT(*)']

  def test_GET_cleanCertificate(self):
    # Test that expired and not valid yet certificates are correctly removed
    # from the DB
    self.put(self.reference)
    self.addExpiredNonvalidyetCertificate(self.reference)

    # There are 3 certificates before doing HTTP GET...
    self.assertEqual(3, self._getDBCertificateCount())

    result = self.requests_get(
      self.kedifa_url + self.reference, cert=self.client_key_pem)

    # ...and only 1 rests after doing so
    self.assertEqual(1, self._getDBCertificateCount())

    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      self.pem,
      result.text
    )

  def test_GET_list_cleanCertificate(self):
    # Test that expired and not valid yet certificates are correctly removed
    # from the DB
    self.put()
    self.addExpiredNonvalidyetCertificate(self.reference)

    # There are 3 certificates before doing HTTP GET...
    self.assertEqual(3, self._getDBCertificateCount())

    result = self.requests_get(
      self.kedifa_url + self.reference + '/list', cert=self.client_key_pem)

    # ...and only 1 rests after doing so
    self.assertEqual(1, self._getDBCertificateCount())

    self.assertEqual(
      httplib.OK,
      result.status_code
    )
    self.assertEqual(
      {"key_list": ["1"]},
      result.json()
    )

  def test_bad_query_string(self):
    result = self.requests_get(self.kedifa_url + '/!?&&==')

    self.assertEqual(
      httplib.BAD_REQUEST,
      result.status_code
    )
    self.assertEqual(
      "Query string '&&==' was not correct.",
      result.text
    )


class KedifaUpdaterMixin(KedifaMixin):
  def setUp(self):
    super(KedifaUpdaterMixin, self).setUp()

    state = tempfile.NamedTemporaryFile(dir=self.testdir, delete=False)
    state.close()
    self.state = state.name

  def setupMapping(self, mapping_content=''):
    mapping = tempfile.NamedTemporaryFile(dir=self.testdir, delete=False)
    mapping.write(mapping_content)
    mapping.close()
    self.mapping = mapping.name


class KedifaUpdaterMappingTest(KedifaUpdaterMixin, unittest.TestCase):
  def test_updateMapping_empty(self):
    self.setupMapping()
    u = updater.Updater(1, self.mapping, self.state, None, None, None, None,
                        True, False)
    u.updateMapping()
    self.assertEqual(u.mapping, {})

  def test_updateMapping_normal(self):
    self.setupMapping('url file')
    u = updater.Updater(1, self.mapping, self.state, None, None, None, None,
                        True, False)
    u.updateMapping()
    self.assertEqual(u.mapping, {'file': ('url', None)})

  def test_updateMapping_morewhite(self):
    self.setupMapping('url \t file')
    u = updater.Updater(1, self.mapping, self.state, None, None, None, None,
                        True, False)
    u.updateMapping()
    self.assertEqual(u.mapping, {'file': ('url', None)})

  def test_updateMapping_one_empty(self):
    self.setupMapping('url file\n     \n')
    u = updater.Updater(1, self.mapping, self.state, None, None, None, None,
                        True, False)
    u.updateMapping()
    self.assertEqual(u.mapping, {'file': ('url', None)})

  def test_updateMapping_one_not_enough(self):
    self.setupMapping('url file\nbuzz\n')
    u = updater.Updater(1, self.mapping, self.state, None, None, None, None,
                        True, False)
    u.updateMapping()
    self.assertEqual(u.mapping, {'file': ('url', None)})

  def test_updateMapping_with_fallback(self):
    self.setupMapping('url file\nbuzz oink fallback\n')
    u = updater.Updater(1, self.mapping, self.state, None, None, None, None,
                        True, False)
    u.updateMapping()
    self.assertEqual(
      u.mapping, {'file': ('url', None), 'oink': ('buzz', 'fallback')})

  def test_updateMapping_one_comment(self):
    self.setupMapping('url file\n#buzz uff\n')
    u = updater.Updater(1, self.mapping, self.state, None, None, None, None,
                        True, False)
    u.updateMapping()
    self.assertEqual(u.mapping, {'file': ('url', None)})


class KedifaUpdaterUpdateCertificateTest(
  KedifaUpdaterMixin, unittest.TestCase):
  def setUp(self):
    super(KedifaUpdaterUpdateCertificateTest, self).setUp()
    certificate_file = tempfile.NamedTemporaryFile(
      dir=self.testdir, delete=True)
    certificate_file.close()
    self.certificate_file_name = certificate_file.name

  def _update(self, certificate, fetch, master_content, fallback=None):
    with open(self.certificate_file_name, 'w') as fh:
      fh.write(certificate)
    fallback_file = None
    if fallback:
      fallback_file = tempfile.NamedTemporaryFile(
        dir=self.testdir, delete=False)
      fallback_file.write(fallback)
      fallback_file.close()
    mapping = 'http://example.com %s' % (self.certificate_file_name,)
    if fallback_file:
      mapping = '%s %s' % (mapping, fallback_file.name)
    self.setupMapping(mapping)
    u = updater.Updater(
      1, self.mapping, self.state, '/master/certificate/file', None, None,
      None, True, False)
    u.updateMapping()
    u.readState()
    with mock.patch.object(
      updater.Updater, 'fetchCertificate', return_value=fetch):
      result = u.updateCertificate(self.certificate_file_name, master_content)
    u.writeState()
    return open(self.certificate_file_name, 'r').read(), result

  def assertState(self, state):
    with open(self.state, 'r') as fh:
      json_state = json.load(fh)
    self.assertEqual(
      json_state,
      state
    )

  def test_nocert_nofetch_nomaster_nofallback(self):
    certificate, update = self._update(
      certificate='', fetch='', master_content=None)
    self.assertEqual('', certificate)
    self.assertFalse(update)
    self.assertState({})

  def test_cert_nofetch_nomaster_nofallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='', master_content=None)
    self.assertEqual('old content', certificate)
    self.assertFalse(update)
    self.assertState({})

  def test_nocert_fetch_nomaster_nofallback(self):
    certificate, update = self._update(
      certificate='', fetch='content', master_content=None)
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})

  def test_cert_fetch_nomaster_nofallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='content', master_content=None)
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})

  def test_nocert_nofetch_master_nofallback(self):
    certificate, update = self._update(
      certificate='', fetch='', master_content='master')
    self.assertEqual('master', certificate)
    self.assertTrue(update)
    self.assertState({})

  def test_cert_nofetch_master_nofallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='', master_content='master')
    self.assertEqual('old content', certificate)
    self.assertFalse(update)
    self.assertState({})

  def test_nocert_fetch_master_nofallback(self):
    certificate, update = self._update(
      certificate='', fetch='content', master_content='master')
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})

  def test_cert_fetch_master_nofallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='content', master_content='master')
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})

  def test_nocert_nofetch_nomaster_fallback(self):
    certificate, update = self._update(
      certificate='', fetch='', master_content=None, fallback='fallback')
    self.assertEqual('fallback', certificate)
    self.assertTrue(update)
    self.assertState({})

  def test_cert_nofetch_nomaster_fallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='', master_content=None,
      fallback='fallback')
    self.assertEqual('fallback', certificate)
    self.assertTrue(update)
    self.assertState({})

  def test_cert_nofetch_nomaster_fallback_overridden(self):
    with open(self.state, 'w') as fh:
      json.dump({self.certificate_file_name: True}, fh)
    certificate, update = self._update(
      certificate='old content', fetch='', master_content=None,
      fallback='fallback')
    self.assertEqual('old content', certificate)
    self.assertFalse(update)
    self.assertState({self.certificate_file_name: True})

  def test_nocert_fetch_nomaster_fallback(self):
    certificate, update = self._update(
      certificate='', fetch='content', master_content=None,
      fallback='fallback')
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})

  def test_cert_fetch_nomaster_fallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='content', master_content=None,
      fallback='fallback')
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})

  def test_nocert_nofetch_master_fallback(self):
    certificate, update = self._update(
      certificate='', fetch='', master_content='master',
      fallback='fallback')
    self.assertEqual('fallback', certificate)
    self.assertTrue(update)
    self.assertState({})

  def test_cert_nofetch_master_fallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='', master_content='master',
      fallback='fallback')
    self.assertEqual('fallback', certificate)
    self.assertTrue(update)
    self.assertState({})

  def test_cert_nofetch_master_fallback_overridden(self):
    with open(self.state, 'w') as fh:
      json.dump({self.certificate_file_name: True}, fh)
    certificate, update = self._update(
      certificate='old content', fetch='', master_content='master',
      fallback='fallback')
    self.assertEqual('old content', certificate)
    self.assertFalse(update)
    self.assertState({self.certificate_file_name: True})

  def test_nocert_fetch_master_fallback(self):
    certificate, update = self._update(
      certificate='', fetch='content', master_content='master',
      fallback='fallback')
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})

  def test_cert_fetch_master_fallback(self):
    certificate, update = self._update(
      certificate='old content', fetch='content', master_content='master',
      fallback='fallback')
    self.assertEqual('content', certificate)
    self.assertTrue(update)
    self.assertState({self.certificate_file_name: True})


class KedifaUpdaterUpdateCertificatePrepareTest(
  KedifaUpdaterMixin, unittest.TestCase):
  def setUp(self):
    super(KedifaUpdaterUpdateCertificatePrepareTest, self).setUp()
    certificate_file = tempfile.NamedTemporaryFile(
      dir=self.testdir, delete=True)
    certificate_file.close()
    self.certificate_file_name = certificate_file.name

  def _prepare(self, certificate, master_content, fallback=None):
    if certificate:
      with open(self.certificate_file_name, 'w') as fh:
        fh.write(certificate)
    fallback_file = None
    if fallback:
      fallback_file = tempfile.NamedTemporaryFile(
        dir=self.testdir, delete=False)
      fallback_file.write(fallback)
      fallback_file.close()
    master_file = '/master/certificate/file'
    if master_content:
      master_file = tempfile.NamedTemporaryFile(
        dir=self.testdir, delete=False)
      master_file.write(master_content)
      master_file.close()
      master_file = master_file.name

    mapping = 'http://example.com %s' % (self.certificate_file_name,)
    if fallback_file:
      mapping = '%s %s' % (mapping, fallback_file.name)
    self.setupMapping(mapping)
    u = updater.Updater(
      1, self.mapping, None, master_file, None, None,
      None, True, True)
    with mock.patch.object(
      updater.Updater, 'fetchCertificate') as fetchCertificate:
      with mock.patch.object(
        updater.Updater, 'writeState') as writeState:
        u.prepare()
    writeState.assert_not_called()
    fetchCertificate.assert_not_called()
    try:
      return open(self.certificate_file_name, 'r').read()
    except IOError:
      return None

  def test_nocert_nomaster_nofallback(self):
    certificate = self._prepare(
      certificate='', master_content=None)
    self.assertEqual(None, certificate)

  def test_nocert_master_nofallback(self):
    certificate = self._prepare(
      certificate='', master_content='master')
    self.assertEqual('master', certificate)

  def test_nocert_nomaster_fallback(self):
    certificate = self._prepare(
      certificate='', master_content=None, fallback='fallback')
    self.assertEqual('fallback', certificate)

  def test_nocert_master_fallback(self):
    certificate = self._prepare(
      certificate='', master_content='master', fallback='fallback')
    self.assertEqual('fallback', certificate)

  def test_cert_nomaster_nofallback(self):
    certificate = self._prepare(
      certificate='cert', master_content=None)
    self.assertEqual('cert', certificate)

  def test_cert_master_nofallback(self):
    certificate = self._prepare(
      certificate='cert', master_content='master')
    self.assertEqual('cert', certificate)

  def test_cert_nomaster_fallback(self):
    certificate = self._prepare(
      certificate='cert', master_content=None, fallback='fallback')
    self.assertEqual('cert', certificate)

  def test_cert_master_fallback(self):
    certificate = self._prepare(
      certificate='cert', master_content='master', fallback='fallback')
    self.assertEqual('cert', certificate)


class KedifaUpdaterLoopTest(
  KedifaUpdaterMixin, unittest.TestCase):

  def test(self):
    u = updater.Updater(
      1, None, self.state, None, None, None, None, True, False)
    lock_file = u.state_lock_file
    os.unlink(self.state)
    self.assertFalse(os.path.exists(lock_file))
    self.assertFalse(os.path.exists(self.state))
    with mock.patch.object(
      updater.Updater, 'prepare') as mock_prepare:
      with mock.patch.object(
        updater.Updater, 'action', return_value=None) as mock_action:
        u.loop()
    mock_prepare.assert_called()
    mock_action.assert_called()
    self.assertFalse(os.path.exists(lock_file))
    self.assertFalse(os.path.exists(self.state))

  def test_raises(self):
    u = updater.Updater(
      1, None, self.state, None, None, None, None, True, False)
    lock_file = u.state_lock_file
    self.assertFalse(os.path.exists(lock_file))
    with mock.patch.object(
      updater.Updater, 'prepare'):
      with mock.patch.object(
        updater.Updater, 'action', side_effect=Exception()) as mock_object:
        self.assertRaises(Exception, u.loop)
    mock_object.assert_called()
    self.assertFalse(os.path.exists(lock_file))

  def test_lock(self):
    u = updater.Updater(
      1, None, self.state, None, None, None, None, True, False)
    lock_file = u.state_lock_file
    lock = zc.lockfile.LockFile(lock_file)
    try:
      self.assertTrue(os.path.exists(lock_file))
      with mock.patch.object(
        updater.Updater, 'action', return_value=None) as mock_object:
        self.assertRaises(SystemExit, u.loop)
      mock_object.assert_not_called()
      self.assertTrue(os.path.exists(lock_file))
    finally:
      lock.close()

  def test_infinite(self):
    u = updater.Updater(
      1, None, self.state, None, None, None, None, False, False)
    lock_file = u.state_lock_file
    os.unlink(self.state)
    self.assertFalse(os.path.exists(lock_file))
    self.assertFalse(os.path.exists(self.state))
    with mock.patch.object(
      updater.Updater, 'prepare', return_value=None) as mock_prepare:
      with mock.patch.object(
        updater.Updater, 'action', return_value=None) as mock_action:
        with mock.patch.object(
          updater.time, 'sleep', side_effect=ValueError('timer')) as timer:
          self.assertRaises(ValueError, u.loop)
    timer.assert_called_with(1)
    mock_prepare.assert_called()
    mock_action.assert_called()
    self.assertFalse(os.path.exists(lock_file))
    self.assertFalse(os.path.exists(self.state))
