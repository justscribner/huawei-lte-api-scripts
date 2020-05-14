import os
import sys
import requests

# load environment variable from .env file
from huawei_lte_api.enums.sms import BoxTypeEnum
from huawei_lte_api.api.User import User
from huawei_lte_api.Connection import Connection
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Client import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from huawei_lte_api.exceptions import ResponseErrorLoginCsfrException
from huawei_lte_api.exceptions import LoginErrorUsernamePasswordWrongException
from math_bands import convert_bands_hex2list

HUAWEI_ROUTER_IP_ADDRESS = os.getenv("HUAWEI_ROUTER_IP_ADDRESS")
HUAWEI_ROUTER_ACCOUNT = os.getenv("HUAWEI_ROUTER_ACCOUNT")
HUAWEI_ROUTER_PASSWORD = os.getenv("HUAWEI_ROUTER_PASSWORD")
GMAIL_ACCOUNT = os.getenv("GMAIL_ACCOUNT")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
MAIL_RECIPIENT = os.getenv("MAIL_RECIPIENT").split(",")
DELAY_SECOND = int(os.getenv("DELAY_SECOND"))


class ModemSession(object):

    def set_login(self, ip=HUAWEI_ROUTER_IP_ADDRESS, login=HUAWEI_ROUTER_ACCOUNT, password=HUAWEI_ROUTER_PASSWORD):
        self.url = 'http://{ip}/'
        self.login = login
        self.password = password

    def init_connection(self):
        connection = AuthorizedConnection(self.url, self.login, self.password)
        self.client = Client(connection)
        self.dialup_status = self.client.dial_up.mobile_dataswitch()

    def close_connection(self):
        self.client.user.logout()

    def check_connection(self):
        try:
            self.init_connection()
            self.close_connection()
        except LoginErrorUsernamePasswordWrongException:
            return {'up': False, 'cause': 'password'}
        except requests.exceptions.ConnectionError:
            return {'up': False, 'cause': 'network'}
        return {'up': True}


from huawei_lte_api.enums.sms import BoxTypeEnum
from huawei_lte_api.api.User import User
from huawei_lte_api.Connection import Connection
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Client import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from huawei_lte_api.exceptions import ResponseErrorLoginCsfrException
from huawei_lte_api.exceptions import LoginErrorUsernamePasswordWrongException
from math_bands import convert_bands_hex2list
