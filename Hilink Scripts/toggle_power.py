#!/usr/bin/env python

import sys
import requests
import xmltodict

TOGGLE = sys.argv[1]


class HuaweiE3372(object):
    BASE_URL = 'http://{host}'
    TOKEN_URL = '/api/webserver/SesTokInfo'
    SWITCH_URL = '/api/dialup/mobile-dataswitch'
    session = None

    def __init__(self, host='192.168.8.1'):
        self.host = host
        self.base_url = self.BASE_URL.format(host=host)
        self.session = requests.Session()

    def switch_modem(self, state=TOGGLE):
        try:
            # Get session and verification tokens from the modem
            r = self.session.get(self.base_url + self.TOKEN_URL, timeout=3)
            _dict = xmltodict.parse(r.text).get('response', None)

            # Build the switch request
            headers = {
                'Cookie': _dict['SesInfo'],
                '__RequestVerificationToken': _dict['TokInfo']
            }

            data = '<?xml version: "1.0" encoding="UTF-8"?><request><dataswitch>' + \
                state + '</dataswitch></request>'

            r = self.session.post(
                self.base_url + self.SWITCH_URL, data=data, headers=headers, timeout=3)
            if r.status_code == 200:
                return True
            else:
                return False

        except Exception as ex:
            print("Failed to switch modem..")
            print(ex)
            return False


def main():
    e3372 = HuaweiE3372()

    # Pass '1' for on
    # Pass '0' for off
    e3372.switch_modem('1')


if __name__ == "__main__":
    main()
