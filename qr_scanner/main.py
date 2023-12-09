from interface import Ui_Form
from PyQt5.QtWidgets import QApplication, QWidget,QMessageBox
from connection import ConnectWorker
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import qrcode,cv2,os
from pyzbar.pyzbar import decode



class QrScannerApp(QWidget):
        def __init__(self) -> None:
            super().__init__()
            self.app = Ui_Form()
            self.app.setupUi(self)
            self.app.manually_btn.clicked.connect(self.conn_manually)
            self.app.connect_qr.clicked.connect(self.connect_with_qr)
            
            
        def wifi_oxu(self,frame):
            barkodlar = decode(frame)
            for barkod in barkodlar:
                if barkod.type == 'QRCODE':
                    wifi_data = barkod.data.decode('utf-8')
                    return wifi_data
            return None
        
        
        
        def update_frame(self):
            
            self.success, self.img = self.cap.read()
            self.img = cv2.flip(self.img, 1)
            
            if self.img is not None:
                
                wifi_data = self.wifi_oxu(self.img)
                if wifi_data:
                    self.cap.release()
                    cv2.destroyAllWindows()
                    try:
                        ssid = wifi_data[wifi_data.index('S:')+2:wifi_data.index(';T')]
                        sifre = wifi_data[wifi_data.index('P:')+2:wifi_data.index(';H')]
                        self.qr_code = qrcode.make(wifi_data)
                        self.path_qr = 'qrcode.png'
                        self.qr_code.save(self.path_qr)
                        pixmap = QPixmap('qrcode.png')
                        self.app.qr_frame.setPixmap(pixmap)
                        os.remove('qrcode.png')
                        self.app.pass_input.setText(sifre)
                        self.app.ssid_input.setText(ssid)
                        QTimer.singleShot(1000, lambda: self.check_wifi_connection(ssid, sifre))
                    except Exception as e:
                        QMessageBox.critical(ekran,'Error',f'QR code cannot read!\n\n{e}')
                        self.cap = cv2.VideoCapture(self.capture_value)
                        
                    
                    
                    
                                    
                else:    
                    height, width, channel = self.img.shape
                    bytes_per_line = 3 * width
                    q_image = QImage(
                        self.img.data, width, height, bytes_per_line, QImage.Format_RGB888
                    ).rgbSwapped()
                    pixmap = QPixmap.fromImage(q_image)
                    self.app.qr_frame.setPixmap(pixmap)
                    self.app.qr_frame.setAlignment(Qt.AlignCenter) #type:ignore
                
        
        def check_wifi_connection(self, ssid_l, sifre_l):
            
            self.worker_thread = ConnectWorker(ssid_l,sifre_l)
            self.worker_thread.succ.connect(self.work_information)
            self.worker_thread.start()
            
        
        def work_information(self,value):
            if value:
                QMessageBox.information(ekran, 'Information', 'Connected to WIFI with success!')
            else:
                QMessageBox.critical(ekran, 'Connection Error', 'Unable to connect to network!')
            
                
        def connect_with_qr(self):
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(int(1000 / 30))
            if self.app.webcam_box.currentIndex() == 0:
                self.capture_value = 0
            else:
                self.capture_value = 1
            self.cap = cv2.VideoCapture(self.capture_value)
        
        
        def conn_manually(self):
            ssid = self.app.ssid_input.text()
            passw = self.app.pass_input.text()
            
            if ssid !='' and passw != '':
                response = QMessageBox.question(
                            ekran,
                            'Connection query','Do you want connect to "{}"'.format(ssid),
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No,
                        )
                if response == QMessageBox.Yes:
                    self.worker_thread = ConnectWorker(ssid,passw)
                    self.worker_thread.succ.connect(self.work_information)
                    self.worker_thread.start()
            else:
                QMessageBox.critical('Connect Error','SSID or Password cannot be left blank!')
        
        
        

app = QApplication([])
ekran = QrScannerApp()
ekran.show()
app.exec_()
