import os
import smtplib
import json
import time
import gettext
import dotenv
import requests

lang = {
    'zh_TW': "zh_TW",
    'zh_HK': "zh_HK",
    'zh_CN': "zh_CN",
    'en_US': "en_US",
}
SET_LANG = os.getenv("LOCALE")
CURRUNT_LOCALE = lang.get(SET_LANG, "en")
t = gettext.translation('messages', 'locale', [CURRUNT_LOCALE])
_ = t.gettext

try:
    import huawei_lte_api
except ImportError:
    print(_('Trying to Install required module: huawei_lte_api'))
    os.system('pip install huawei_lte_api')
try:
    import dotenv
except ImportError:
    print(_('Trying to Install required module: python-dotenv'))
    os.system('pip install python-dotenv')
from dotenv import load_dotenv
load_dotenv()

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


# load environment variable from .env file
HUAWEI_ROUTER_IP_ADDRESS = os.getenv("HUAWEI_ROUTER_IP_ADDRESS")
HUAWEI_ROUTER_ACCOUNT = os.getenv("HUAWEI_ROUTER_ACCOUNT")
HUAWEI_ROUTER_PASSWORD = os.getenv("HUAWEI_ROUTER_PASSWORD")
GMAIL_ACCOUNT = os.getenv("GMAIL_ACCOUNT")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
MAIL_RECIPIENT = os.getenv("MAIL_RECIPIENT").split(",")
DELAY_SECOND = int(os.getenv("DELAY_SECOND"))


def get_signal_int(value):
    return int(value.split('d')[0])


class HuaweiMain():
    def set_login(self, ip, login, password):
        self.url = f'http://{ip}/'
        self.login = login
        self.password = password

    def init_connection(self):
        connection = AuthorizedConnection(self.url, self.login, self.password)
        self.client = Client(connection)

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

    def init_net_mode(self):
        self.net_mode = self.client.net.net_mode()
        self.network_mode = self.net_mode['NetworkMode']
        self.network_band = self.net_mode['NetworkBand']
        self.lte_band = self.net_mode['LTEBand']

    def get_bands_number(self):
        try:
            self.init_connection()
            self.init_net_mode()
            self.close_connection()
        except LoginErrorUsernamePasswordWrongException:
            return False
        return self.lte_band

    def set_bands_number(self, number):
        try:
            self.init_connection()
            self.init_net_mode()
            self.lte_band = number
            self.client.net.set_net_mode(
                self.lte_band, self.network_band, self.network_mode)
            self.close_connection()
        except LoginErrorUsernamePasswordWrongException:
            return False

    def get_upload_band(self):
        try:
            self.init_connection()
            self.signal_info = self.client.device.signal()
            self.close_connection()
            return self.signal_info['band']
        except LoginErrorUsernamePasswordWrongException:
            return False

    def get_traffic_statistics(self):
        self.traffic_info = self.client.monitoring.traffic_statistics()

    # in bps
    def get_download_rate(self):
        return int(self.traffic_info['CurrentDownloadRate']) * 8

    # in bps
    def get_upload_rate(self):
        return int(self.traffic_info['CurrentUploadRate']) * 8

    def get_all_monitor_information(self):
        try:
            self.init_connection()
            signal_info = self.client.device.signal()
            net_mode = self.client.net.net_mode()
            self.get_traffic_statistics()
            self.close_connection()
            info_dict = {
                'upload_band': 'b' + signal_info['band'],
                'download_band': convert_bands_hex2list(net_mode['LTEBand']),
                'upload_rate': self.get_upload_rate(),
                'download_rate': self.get_download_rate(),
                'rsrq': get_signal_int(signal_info['rsrq']),
                'sinr': get_signal_int(signal_info['sinr']),
                'rsrp': get_signal_int(signal_info['rsrp']),
            }
            return info_dict
        except LoginErrorUsernamePasswordWrongException:
            return False


#     # Use infinite loop to check SMS
# while True:
#     try:
#         # Establish a connection with authorized
#         connection = AuthorizedConnection('http://{}:{}@{}/'.format(
#             HUAWEI_ROUTER_ACCOUNT, HUAWEI_ROUTER_PASSWORD, HUAWEI_ROUTER_IP_ADDRESS))
#         client = Client(connection)
#         # Set account phone number to pass on to the sms email
#         ACCOUNT_PHONE_NUMBER = client.device.information()['Msisdn']
#         # print(ACCOUNT_PHONE_NUMBER)
#         # get first SMS(unread priority)
#         sms = client.sms.get_sms_list(1, BoxTypeEnum.LOCAL_INBOX, 1, 0, 0, 1)
#         # Skip this loop if the SMS was read
#         if int(sms['Messages']['Message']['Smstat']) == 1:
#             # Logout
#             client.user.logout()
#             # Inspection interval(second)
#             time.sleep(DELAY_SECOND)
#             continue

#         # Find a new SMS, go send e-mail！
#         print(_('{Date} Find a new SMS ID:{Message_Index}! from {Phone_Number}').format(
#             Date=sms['Messages']['Message']['Date'], Message_Index=sms['Messages']['Message']['Index'], Phone_Number=sms['Messages']['Message']['Phone']))

#         # send e-mail
#         msg = MIMEMultipart()
#         msg['Subject'] = _('You have a message from {Phone_Number} TO {Account_Phone_Number}').format(
#             Phone_Number=sms['Messages']['Message']['Phone'], Account_Phone_Number=ACCOUNT_PHONE_NUMBER)
#         body = _('Message date: {Date}\nAccount Phone Number: {Account_Phone_Num}\nMessage content：\n\n {Content}').format(
#             Date=sms['Messages']['Message']['Date'], Account_Phone_Num=ACCOUNT_PHONE_NUMBER, Content=sms['Messages']['Message']['Content'])
#         msg.attach(MIMEText(body, 'plain'))

#         try:
#             server = smtplib.SMTP('smtp.gmail.com', 587)
#             server.ehlo()
#             server.starttls()
#             server.ehlo()
#             server.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
#             server.sendmail(GMAIL_ACCOUNT, MAIL_RECIPIENT, msg.as_string())
#             server.quit()
#             print(_('ID:{Message_Index} from {Phone_Number} was successfully sent!').format(
#                 Message_Index=sms['Messages']['Message']['Index'], Phone_Number=sms['Messages']['Message']['Phone']))
#             # Set the SMS status was read
#             client.sms.set_read(int(sms['Messages']['Message']['Index']))
#             # Logout
#             client.user.logout()
#         except Exception as e:
#             client.user.logout()
#             print(_('ID:{Message_Index} from {Phone_Number} failed to send! \nError message:\n{error_msg}').format(
#                 Message_Index=sms['Messages']['Message']['Index'], Phone_Number=sms['Messages']['Message']['Phone'], error_msg=e))
#     except Exception as e:
#         print(_('Router connection failed! Please check the settings. \nError message:\n{error_msg}').format(
#             error_msg=e))
