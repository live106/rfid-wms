from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5 import QtGui

from auto_express import create_express_printer, Express

class PrintThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, printer):
        super().__init__()
        self.printer = printer
        self._stop = False

    def run(self):
        result = self.printer.print_express()
        self.finished.emit(result)

    def stop(self):
        self._stop = True        

class OutStorage(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.initUI()

    def initUI(self):
        # Create a subpage for 出库管理
        # self.label = QLabel("出库管理")
        # self.label.setFixedHeight(30)
        # self.label.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))

        self.print_button = QPushButton("自动打印快递单功能测试", self)
        self.print_button.clicked.connect(self.on_print_button_clicked)
        self.print_button.setFont(QtGui.QFont("Arial", 20))

        vbox = QVBoxLayout()
        # vbox.addWidget(self.label)
        vbox.addWidget(self.print_button)
        self.setLayout(vbox)

    @pyqtSlot()
    def on_print_button_clicked(self):
        # printer = create_express_printer(Express.KURONEKOYAMATO.value)
        printer = create_express_printer(Express.SAGAWAEXP.value)
        self.thread = PrintThread(printer)
        self.thread.finished.connect(self.on_print_finished)
        self.thread.start()        
        
    def on_print_finished(self, result):
        if result:
            QMessageBox.information(self, "成功", "打印快递单成功！")
        else:
            QMessageBox.warning(self, "警告", "打印快递单失败，请重试！")

    def closeEvent(self, event):
        if self.thread is not None:
            self.thread.stop()
            self.thread.wait()
        event.accept()            
        