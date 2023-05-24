from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit, QComboBox, QHBoxLayout, QTableWidget, QFrame, QFileDialog, QTableWidgetItem, QLCDNumber, QHeaderView
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QObject
from PyQt5 import QtGui
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, numbers
import threading
import time
import datetime

from auto_express import create_express_printer, Express
from database import add_orders, get_orders, get_orders_by_order_no, get_epc_barcode_counts, get_orders_by_order_nos
import rfid_api
from rfid_api import stop_async_inventory_event

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
        
class OrderWorker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(list)

    def __init__(self, order_no):
        super().__init__()
        self.order_no = order_no

    def run(self):
        result = get_orders_by_order_no(self.order_no)
        self.result.emit(result)
        self.finished.emit()

class OutboundWorker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(list)

    def __init__(self, order_numbers):
        super().__init__()
        self.order_numbers = order_numbers

    def run(self):
        result = get_orders_by_order_nos(self.order_numbers)
        self.result.emit(result)
        self.finished.emit()

class OutStorage(QWidget):

    counter_updated = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.order_thread = None
        self.order_worker = None

        self.outbound_thread = None
        self.outbound_worker = None

        self.inventoring = False 
        self.epc_list = []
        self.inventory_duration_ref = [0]
        self.counter_updated.connect(self.updateCounter)

        # Create a thread to update the counter every N seconds
        self.counter_thread = threading.Thread(target=self.updateCounterThread)
        # self.counter_thread.daemon = True

        # Create a thread to call rfid_api.get_epc_list
        self.rfid_thread = threading.Thread(target=self.getEpcListThread)
        # self.rfid_thread.daemon = True

        self.current_order_match_data = []

        self.initUI()

    def initUI(self):
        '''
        # Create a subpage for 出库管理
        # self.label = QLabel("出库管理")
        # self.label.setFixedHeight(30)
        # self.label.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))

        self.print_button = QPushButton("自动打印快递单功能测试", self)
        self.print_button.setFont(QtGui.QFont("Arial", 20))
        self.print_button.clicked.connect(self.print_express)

        vbox = QVBoxLayout()
        # vbox.addWidget(self.label)
        vbox.addWidget(self.print_button)
        self.setLayout(vbox)
        '''

        # Add the top row of buttons and input components
        self.order_input = QLineEdit()
        self.order_input.setPlaceholderText('Please enter OrderNo')
        self.order_input.setFont(QtGui.QFont("Arial", 16))
        self.order_input.textChanged.connect(self.on_order_input_changed)

        # Create a button to start inventory
        self.inventory_button = QPushButton("START")
        self.inventory_button.setFont(QtGui.QFont("Arial", 16))
        self.inventory_button.clicked.connect(self.startAsyncInventory)

        # Create a text counter to show the number of characters in the product name input box
        self.counter = QLCDNumber()

        self.express_combo = QComboBox()
        self.express_combo.setPlaceholderText('Plese select express')
        self.express_combo.setFont(QtGui.QFont("Arial", 16))
        # 添加枚举类成员值作为选项
        for express in Express:
            self.express_combo.addItem(express.value)
        # 设置默认选中的枚举类成员
        self.express_combo.setCurrentText(Express.SAGAWAEXP.value)

        self.outbound_button = QPushButton("Outbound")
        self.outbound_button.setFont(QtGui.QFont("Arial", 16))
        self.outbound_button.setEnabled(False)
        self.outbound_button.clicked.connect(self.outbound)

        top_hbox = QHBoxLayout()
        top_hbox.addWidget(self.order_input, 1)
        top_hbox.addWidget(self.inventory_button, 1)
        top_hbox.addWidget(self.counter, 1)
        top_hbox.addWidget(self.express_combo, 1)
        top_hbox.addWidget(self.outbound_button, 1)

        # Add the first table
        self.match_table = QTableWidget()
        self.match_table.setColumnCount(5)
        self.match_table.setHorizontalHeaderLabels(["OrderNo", "JAN", "Qty", "CurrentQty", "Matching"])
        self.match_table.setFixedHeight(260)
        self.match_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add the separator and second set of buttons and table
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        import_button = QPushButton("Import Orders")
        import_button.setFont(QtGui.QFont("Arial", 14))
        import_button.clicked.connect(self.import_data)

        template_button = QPushButton("Download Template")
        template_button.setFont(QtGui.QFont("Arial", 14))
        template_button.clicked.connect(self.download_template)

        self.order_table = QTableWidget()
        headers = ['Type', 'JAN', 'Expiration', 'ZIP', 'Address', 'Name', 'TEL', 'Text1', 'Text2', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'CustomerOrderID', 'Qty', 'OutboundStatus', 'ExpressNo', 'ExpressTime', 'OrderNo']
        self.order_table.setColumnCount(len(headers))
        self.order_table.setHorizontalHeaderLabels(headers)
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        vbox = QVBoxLayout()
        # vbox.addWidget(self.label)
        vbox.addLayout(top_hbox)
        vbox.addWidget(self.match_table)
        vbox.addWidget(separator)

        top_hbox = QHBoxLayout()
        top_hbox.addWidget(import_button, 1)
        top_hbox.addWidget(template_button, 1)

        vbox.addLayout(top_hbox)
        vbox.addWidget(self.order_table)
        self.setLayout(vbox)

        self.reload_orders()

    @pyqtSlot()
    def print_express(self):
        printer = create_express_printer(self.express_combo.currentText())
        self.order_thread = PrintThread(printer)
        self.order_thread.finished.connect(self.on_print_finished)
        self.order_thread.start()
        
    def on_print_finished(self, result):
        if result:
            QMessageBox.information(self, "Success", "Print Express Bill Successful !")
        else:
            QMessageBox.warning(self, "Warning", "Print Express Bill Failure, Please Rety !")

    def closeEvent(self, event):
        if self.order_thread is not None:
            self.order_thread.stop()
            self.order_thread.wait()
        event.accept()            
        
    def download_template(self):
        # Prompt the user to select a location to save the file
        file_path, _ = QFileDialog.getSaveFileName(None, "Save Template", "", "Excel Files (*.xlsx)")

        # Create a new Excel workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Add the desired headers to the worksheet
        headers = ['Type', 'JAN', 'Expiration', 'ZIP', 'Address', 'Name', 'TEL', 'Text1', 'Text2', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'CustomerOrderID', 'Qty', 'OrderNo']
        for i, header in enumerate(headers):
            cell = worksheet.cell(row=1, column=i+1)
            cell.value = header

        # Save the workbook to the selected location
        workbook.save(file_path)

    def import_data(self):
        # Prompt the user to select an Excel file to import
        file_path, _ = QFileDialog.getOpenFileName(None, "Import Data", "", "Excel Files (*.xlsx)")

        # Load the workbook and select the first worksheet
        workbook = openpyxl.load_workbook(file_path)
        worksheet = workbook.active

        # Get the headers from the worksheet
        headers = [cell.value for cell in worksheet[1]]

        # Compare the headers to the headers of the corresponding table in your UI
        expected_headers = ['Type', 'JAN', 'Expiration', 'ZIP', 'Address', 'Name', 'TEL', 'Text1', 'Text2', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'CustomerOrderID', 'Qty', 'OrderNo']
        if headers != expected_headers:
            QMessageBox.warning(None, "Error", "The headers in the selected file do not match the expected headers.")
            return

        # Import the data from the worksheet into the database
        data = []
        for row in worksheet.iter_rows(min_row=2):
            item = {}
            for index, cell in enumerate(row):
                item[headers[index]] = str(cell.value)
            data.append(item)
        add_orders(data)

        # Reload the orders in the UI
        self.reload_orders()

    def reload_orders(self):
        orders = get_orders()
        self.order_table.setRowCount(len(orders))
        for i, order in enumerate(orders):
            for j in range(self.order_table.columnCount()):  # Iterate over the column count
                header = self.order_table.horizontalHeaderItem(j)
                key = header.text()
                value = order.get(key, '')
                item = QTableWidgetItem(str(value))
                self.order_table.setItem(i, j, item)

    @pyqtSlot()
    def on_order_input_changed(self):
        self.current_order_match_data.clear()
        order_no = self.order_input.text()
        if order_no:
            self.order_thread = QThread()
            self.order_worker = OrderWorker(order_no)
            self.order_worker.moveToThread(self.order_thread)
            self.order_thread.started.connect(self.order_worker.run)
            self.order_worker.finished.connect(self.order_thread.quit)
            self.order_worker.finished.connect(self.order_worker.deleteLater)
            self.order_thread.finished.connect(self.order_thread.deleteLater)
            self.order_worker.result.connect(self.update_match_table)
            self.order_thread.start()
        else:
            self.match_table.setRowCount(0)

    def update_match_table(self, result):
        self.current_order_match_data = result
        self.match_table.setRowCount(len(self.current_order_match_data))
        all_match = True
        for i, row in enumerate(result):
            self.match_table.setItem(i, 0, QTableWidgetItem(row["OrderNo"]))
            self.match_table.setItem(i, 1, QTableWidgetItem(row["JAN"]))
            self.match_table.setItem(i, 2, QTableWidgetItem(str(row["Qty"])))
            self.match_table.setItem(i, 3, QTableWidgetItem(str(row.get('CurrentQty', 0))))
            self.match_table.setItem(i, 4, QTableWidgetItem(str(row.get('Matching', False))))
            match = row["Qty"] == row.get('CurrentQty', 0)
            self.match_table.setItem(i, 4, QTableWidgetItem(str(match)))
            if not match:
                all_match = False

        self.outbound_button.setEnabled(all_match)

    def startAsyncInventory(self):
        self.counter_updated.emit(0)
        stop_async_inventory_event.clear()  # Unset the threading.Event object to resume the inventory process
        # self.inventory_button.setEnabled(False)
        self.inventory_button.disconnect()
        self.inventory_button.setText(f"STOP")  # Add this line to set the text of the inventory_button to "结束盘点"
        self.inventory_button.clicked.connect(self.stopAsyncInventory)  # Add this line to set the stop_async_inventory_event value to True when the button is clicked        
        if not self.counter_thread.is_alive():
            self.counter_thread = threading.Thread(target=self.updateCounterThread)
        if not self.rfid_thread.is_alive():
            self.rfid_thread = threading.Thread(target=self.getEpcListThread)
        self.inventoring = True
        self.counter_thread.start()
        self.rfid_thread.start()  # start the rfid_thread        

    def stopAsyncInventory(self):
        stop_async_inventory_event.set()  # Set the threading.Event object to True to stop the inventory process
        self.inventoring = False
        self.inventory_duration_ref = [0]
        self.counter_thread.join()
        
        self.inventory_button.setText("START")
        self.inventory_button.clicked.connect(self.startAsyncInventory)

    def getEpcListThread(self):
        rfid_api.async_get_epc_list(self.epc_list, self.inventory_duration_ref)  # call rfid_api.async_get_epc_list in a new thread
        self.counter_updated.emit(len(self.epc_list))
        self.stopAsyncInventory()       

    def updateCounterThread(self):
        while self.inventoring:
            try:
                time.sleep(1)
                self.counter_updated.emit(len(self.epc_list))
                self.inventory_button.setText(f"STOP[{(str(round(self.inventory_duration_ref[0])) + 's') if self.inventory_duration_ref[0] > 0 else ''}]")  # Add this line to set the text of the inventory_button to "结束盘点"
                print(f"Counter updated: {len(self.epc_list)}, inventory_duration_ref: {self.inventory_duration_ref[0]}")
                if not self.counter_thread.is_alive():
                    print("Counter thread terminated.")
                    break
            except Exception as e:
                error_message = str(e)
                print(error_message)
                pass
        print("Counter updated done.")

    def updateCounter(self, value):
        self.counter.display(value)
        if len(self.epc_list) > 0:
            result = get_epc_barcode_counts(self.epc_list)
            print('result: ', result)
            for v in self.current_order_match_data:
                v['CurrentQty'] = result.get(v['JAN'], 0)
            self.update_match_table(self.current_order_match_data)

    def outbound(self):
        order_numbers = []
        for row in range(self.match_table.rowCount()):
            order_number_item = self.match_table.item(row, 0)
            if order_number_item is not None:
                order_numbers.append(order_number_item.text())

        if order_numbers:
            self.outbound_thread = QThread()
            self.outbound_worker = OutboundWorker(order_numbers)
            self.outbound_worker.moveToThread(self.outbound_thread)
            self.outbound_thread.started.connect(self.outbound_worker.run)
            self.outbound_worker.finished.connect(self.outbound_thread.quit)
            self.outbound_worker.finished.connect(self.outbound_worker.deleteLater)
            self.outbound_thread.finished.connect(self.outbound_thread.deleteLater)
            self.outbound_worker.result.connect(self.handle_outbound_result)            
            self.outbound_thread.start()

    def handle_outbound_result(self, outbound_orders):
        print('outbound_orders: ', outbound_orders)
        self.save_outbound_excel_for_express(outbound_orders)
        self.print_express()

    def save_outbound_excel_for_express(self, outbound_orders):
        # Create a new Excel workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Define the desired column headers
        headers = [
            "出荷予定日", "送り状種類", "OrNO", "郵便番号", "住所1", "住所2",
            "名前", "電話", "Comment1", "Comment2", "Text1", "口数",
            "発注番号", "Na", "YYU", "JYU", "JYU2", "TT"
        ]

        # Add the headers to the worksheet
        for col_num, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = header
            cell.alignment = Alignment(horizontal='center')

            # Adjust the column width to fit the content
            column_letter = get_column_letter(col_num)
            worksheet.column_dimensions[column_letter].bestFit = True

        # Set the number format for the "出荷予定日" column
        date_format = 'yyyy/m/d'
        worksheet.column_dimensions['A'].number_format = numbers.FORMAT_DATE_YYYYMMDD2

        # Populate the worksheet with order data
        for row_num, order in enumerate(outbound_orders, 2):
            # 获取当前日期
            current_date = datetime.date.today()
            formatted_date = current_date.strftime("%Y/%m/%d").replace('/0', '/')
            worksheet.cell(row=row_num, column=1, value=formatted_date)
            # worksheet.cell(row=row_num, column=1, value=order.get("D_Date", ""))
            worksheet.cell(row=row_num, column=2, value=order.get("Type", ""))
            worksheet.cell(row=row_num, column=3, value=order.get("OrderNo", ""))
            worksheet.cell(row=row_num, column=4, value=order.get("ZIP", ""))
            worksheet.cell(row=row_num, column=5, value=order.get("Address", ""))
            worksheet.cell(row=row_num, column=6, value=order.get("Address", ""))
            worksheet.cell(row=row_num, column=7, value=order.get("Name", ""))
            worksheet.cell(row=row_num, column=8, value=order.get("TEL", ""))
            worksheet.cell(row=row_num, column=9, value=order.get("Text1", ""))
            worksheet.cell(row=row_num, column=10, value=order.get("Text2", ""))
            worksheet.cell(row=row_num, column=11, value=order.get("Text1", ""))
            worksheet.cell(row=row_num, column=12, value=order.get("口数", ""))
            worksheet.cell(row=row_num, column=13, value=order.get("発注番号", ""))
            worksheet.cell(row=row_num, column=14, value=order.get("ShipperName", ""))
            worksheet.cell(row=row_num, column=15, value=order.get("ShipperZIP", ""))
            worksheet.cell(row=row_num, column=16, value=order.get("ShipperAddress", ""))
            worksheet.cell(row=row_num, column=17, value=order.get("ShipperAddress", ""))
            worksheet.cell(row=row_num, column=18, value=order.get("ShipperTel", ""))

        # Save the workbook
        file_path = "./order_for_express.xlsx"
        workbook.save(file_path)