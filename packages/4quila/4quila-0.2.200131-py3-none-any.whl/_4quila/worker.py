#!/usr/bin/env python
# coding: utf-8
import smtplib
import requests
import json
import os
import tempfile
import fcntl
import sys
from .common import EMAIL
from .common import logger
from email.parser import Parser
from email.header import decode_header

email_address = 'tzeng@cobo.com'
email_server = 'smtp.exmail.qq.com'
email_password = ''


def send_email(subject, message, to_address):
    assert email_server
    assert email_password
    base_address = EMAIL
    from_address = email_address
    header = ["From:" + base_address, 'To:' + to_address, 'Subject:' + subject]
    message = '\r\n\r\n'.join(['\r\n'.join(header), '\r\n'.join(message.split('\n'))])
    smtp = smtplib.SMTP(email_server)
    smtp.login(from_address, email_password)
    smtp.sendmail(from_address, to_address, message)
    smtp.quit()


def parse_mail(message):

    def _parse(_message):
        if _message.is_multipart():
            return [_parse(i) for i in _message.get_payload()]
        else:
            if _message.get_content_type() in ['text/plain', 'text/html']:
                return _message.get_payload(decode=True).decode('utf-8')
            else:
                filename = _message.get_filename()
                assert filename
                return _message.get_payload(decode=True)

    result = {}
    message = Parser().parsestr(message)
    for field in ['From', 'To', 'Subject']:
        value, coding = decode_header(message.get(field, ''))[0]
        if coding:
            print(value)
            assert isinstance(value, bytes)
            result[field] = value.decode(coding)
        else:
            result[field] = value

    result['Message'] = _parse(message)

    return result


class Session(object):
    def __init__(self, domain, cookies={}, headers={}):
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/69.0.3497.81 Chrome/69.0.3497.81 Safari/537.36'
        self._session = requests.session()
        self.domain = domain
        self.cookies = cookies
        self.headers = headers

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _request(self, method, path, params={}, data={}, headers={}):
        logger.info(
            '%s ing %s' % (
                method, self.domain + path,
            )
            + (' params %s' % params if params else '')
            + (' data %s' % data if data else '')
            + (' headers %s' % headers if headers else '')
        )
        headers.update(self.headers)
        response = self._session.request(method, self.domain + path, data=json.dumps(data), params=params, cookies=self.cookies, headers=headers)
        try:
            response_json = response.json()
            logger.info('responding json:\n%s' % json.dumps(response_json, indent=4))
            return response_json
        except Exception:
            logger.info('responding text:\n%s' % (''.join(response.text.splitlines())))
            return response.text

    def get(self, path, params={}, headers={}):
        return self._request('GET', path, params=params, headers=headers)

    def post(self, path, data={}, headers={}):
        return self._request('POST', path, data=data, headers=headers)

    def head(self, path, params={}, headers={}):
        return self._request('HEAD', path, params=params, headers=headers)


class Lock(object):
    def __init__(self, locker_id):
        basename = 'locker_%s.lock' % locker_id
        self.lockfile = os.path.normpath(tempfile.gettempdir() + '/' + basename)
        self.fp = open(self.lockfile, 'w')
        try:
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except Exception:
            sys.exit(-1)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.lockf(self.fp, fcntl.LOCK_UN)
        if os.path.isfile(self.lockfile):
            os.unlink(self.lockfile)


if __name__ == '__main__':
    import _4quila
    with open('/home/t10n/test_email_back', 'r') as tm:
        print(parse_mail(tm.read()))
