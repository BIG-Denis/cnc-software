from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5 import uic
from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtGui import QTextCursor
from PIL import Image, ImageDraw
import sys
#import serial.tools.list_ports as get_list

def SendGcode(port: str, gcodeLines: list[str], baudrate: int, chunkSize: int=250, retries: int=3) -> bool:
    print(f"Sending G-codes: port={port}, baudrate={baudrate}; G-codes=\n{gcodeLines}")
    return True


def confirm(parent=None, text="Точно?") -> bool:
    return QMessageBox.question(parent, "Подтверждение", text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes


class GraphicsViewClickFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            pos = event.pos()
            print(f"x={pos.x()}, y={pos.y()}")
        return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.mainTabs.setCurrentIndex(1)
        self.GetCOMPorts()
        self.filter = GraphicsViewClickFilter()
        self.field_view.viewport().installEventFilter(self.filter)

        self.btn_colebrate.clicked.connect(self.clicked_btn_calibrate)
        self.btn_clear_img.clicked.connect(self.clicked_btn_clear_img)
        self.btn_g00.clicked.connect(self.clicked_btn_g00)
        self.btn_g01.clicked.connect(self.clicked_btn_g01)
        # TBD

        self.mode: str = 'G00'  # G00, G01, G02, G03, G90, G91
        self.current_x: int = 0
        self.current_y: int = 0
        self.goto_x: int = None
        self.goto_y: int = None
        self.draw_gcodes: list = []

    def draw_img(self):
        print("Image cleared")
        self.img = Image.new("RGB", (330, 228), "white")
        self.draw = ImageDraw.Draw(self.img)
        # self.mode_label.setText(f'Режим: {self.mode}')
        # r = 5  # радиус точки
        # self.draw.ellipse((self.goto_x - r, self.goto_y - r, self.goto_x + r, self.goto_y + r), fill="black")
        self.img.save(".field_img.png")

    def GetCOMPorts(self):
        self.getPorts = QSerialPortInfo()
        ports = list(self.getPorts.availablePorts())
        if ports:
            self.Append('<<<<ПОРТЫ НАЙДЕНЫ>>>>\n')
            self.Append('Список портов:\n')
            for port in ports:
                self.portsComboBox.addItem(port.portName())
                self.Append(port.portName())
            self.Append('\n<<<<ВЫПАДАЮЩИЙ СПИСОК ЗАПОЛНЕН ВСЕМИ ДОСТУПНЫМИ ПОРТАМИ>>>>\n')
        else:
            self.Append('<<<<ПОРТЫ НЕ ОБНАРУЖЕНЫ>>>>\n')

    def Append(self, text):
        cursor = self.consoleEdit.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.consoleEdit.moveCursor(QTextCursor.End)

    def clicked_btn_calibrate(self):
        if not confirm(self, "Вы уверены, что хотите выполнить калибровку?"):
            return
        self.current_x: int = 0
        self.current_y: int = 0
        SendGcode(self.portsComboBox.currentText(), "G00 X0 Y0", int(self.baudRateLineEdit.text()))

    def clicked_btn_clear_img(self):
        if not confirm(self, "Вы уверены, что хотите очистить картинку?"):
            return
        self.goto_x = None
        self.goto_y = None
        self.draw_gcodes = []
        self.draw_img()

    def clicked_btn_g00(self):
        self.mode = 'G00'
        self.mode_label.setText(f'Режим: {self.mode}')

    def clicked_btn_g01(self):
        self.mode = 'G01'
        self.mode_label.setText(f'Режим: {self.mode}')

    def clicked_btn_g02(self):
        pass

    def clicked_btn_g03(self):
        pass

    def clicked_btn_g90(self):
        pass

    def clicked_btn_g91(self):
        pass

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        current_encoding = 'cp1251'
    else:
        current_encoding = 'utf8'

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
