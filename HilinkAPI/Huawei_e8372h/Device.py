

class Device(object):

def toggle_lte(self):
    try:
        self.init_connection()
        if self.dialup_status == 0:
            self.close_connection()
            return self.client.dial_up.set_mobile_dataswitch(1)
        else:
            self.close_connection()
            return self.client.dial_up.set_mobile_dataswitch(0)
    except LoginErrorUsernamePasswordWrongException:
        return False


def reboot_modem(self):
    try:
        self.init_connection()
        self.client.device.control(1)
        self.close_connection()
    except LoginErrorUsernamePasswordWrongException:
        return False
