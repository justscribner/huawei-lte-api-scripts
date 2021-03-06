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

from ModemSession import *
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


def get_signal_int(value):
    return int(value.split('d')[0])


class Monitor(object):

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
