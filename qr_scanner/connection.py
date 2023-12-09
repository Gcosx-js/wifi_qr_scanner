import time
from pywifi import PyWiFi, const
import pywifi
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class ConnectWorker(QThread):
    
    succ  = pyqtSignal(bool)
    
    def __init__(self,ssid,sifre):
        super().__init__()
        self.ssid = ssid
        self.password = sifre
        
        
    def run(self):
        wifi = PyWiFi()
        iface = wifi.interfaces()[0]
        iface.disconnect()

        time.sleep(1)

        profile = pywifi.Profile()
        profile.ssid = self.ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP

        profile.key = self.password  # Wi-Fi şifresi

        tmp_profile = iface.add_network_profile(profile)

        iface.connect(tmp_profile)

        time.sleep(5)

        if iface.status() == const.IFACE_CONNECTED:
            self.succ.emit(True)
        else:
            self.succ.emit(False)