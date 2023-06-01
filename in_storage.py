from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLCDNumber, QHBoxLayout, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
import database
import time
from datetime import datetime

import rfid_api
from rfid_api import stop_async_inventory_event
import threading

class InStorage(QWidget):

    counter_updated = pyqtSignal(int)

    def __init__(self):
        super().__init__()
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

        self.initUI()

    def initUI(self):
        # Create a subpage for 入库管理
        # self.label = QLabel("入库管理")
        # self.label.setFixedHeight(30)
        # self.label.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
        
        # Create a table widget to display some data
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Product Name", "Quantity", "Inbound Time", "Operations"])
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(30)

        # Create a barcode input widget
        self.barcode_input = QComboBox(self)
        self.barcode_input.setPlaceholderText("Please enter barcode")
        self.barcode_input.setFont(QtGui.QFont("Arial", 16))
        self.barcode_input.setEditable(True)
        # Set focus to barcode_input
        self.barcode_input.setFocus(True)
        # self.barcode_input.setFixedHeight(60) # Add this line to set the height of the barcode input box to 60
        self.barcode_input.currentIndexChanged.connect(self.updateProductName)
        self.barcode_input.currentTextChanged.connect(self.updateProductName)

        # Create a product name input widget
        self.product_name_input = QComboBox(self)
        self.product_name_input.setPlaceholderText("Please enter product name")
        self.product_name_input.setFont(QtGui.QFont("Arial", 16))
        self.product_name_input.setEditable(True)
        # self.product_name_input.setFixedHeight(60) # Add this line to set the height of the product name input box to 60
        self.product_name_input.currentIndexChanged.connect(self.updateBarcode)
        self.product_name_input.currentTextChanged.connect(self.updateBarcode)        

        # Create a text counter to show the number of characters in the product name input box
        self.counter = QLCDNumber()

        # Create a button to perform some action
        self.inbound_button = QPushButton("Inbound")
        self.inbound_button.setFont(QtGui.QFont("Arial", 16))
        self.inbound_button.clicked.connect(self.addInbound)
        self.inbound_button.setEnabled(False)

        # Create a button to start inventory
        self.inventory_button = QPushButton("START")
        self.inventory_button.setFont(QtGui.QFont("Arial", 16))
        self.inventory_button.clicked.connect(self.startAsyncInventory)
        # self.inventory_button.clicked.connect(self.startSyncInventory)

        # Set the subpage layout
        vbox = QVBoxLayout()
        # vbox.addWidget(self.label)

        # Create a horizontal layout to hold the product name input box, the barcode input box, the counter, and the button
        hbox = QHBoxLayout()

        # Add the inventory_button widget to the horizontal layout
        hbox.addWidget(self.inventory_button, 1)

        # Add the product name input widget and the barcode input widget to the horizontal layout
        hbox.addWidget(self.barcode_input, 1)
        hbox.addWidget(self.product_name_input, 1)

        # Add the counter and the inbound_button to the horizontal layout
        hbox.addWidget(self.counter, 1)
        hbox.addWidget(self.inbound_button, 1)

        # Add the horizontal layout to the vertical layout
        vbox.addLayout(hbox)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

        # Call the create_table function from database module to create a table if it does not exist 
        database.create_table()

        # Call the delete_old_data function from database module to delete data that are older than 2 days 
        database.delete_old_data()

        self.updateInputOptions()
        self.reloadTable()

    def showEvent(self, event):
        # Set focus to barcode_input when the UI is shown
        self.barcode_input.setFocus()
        event.accept()        

    def updateCounter(self, value):
        self.counter.display(value)

    def addInbound(self):
        if not self.epc_list:
            QMessageBox.warning(self, "WARNING", "epc list is empty, please retry !")
            return
        barcode = self.barcode_input.currentText()
        name = self.product_name_input.currentText()
        quantity = str(self.counter.value())
        if barcode:
            inbound_id = database.add_inbound(barcode, name, quantity)
            database.add_epcs(self.epc_list, barcode, name, inbound_id)
            if name:
                # Check if the product exists in the "products" table
                product_name = database.get_product_name(barcode)
                # If the product does not exist, add it to the "products" table
                if not product_name:
                    database.add_product(barcode, name)
                # If the product name does not match current name, update the "products" table
                elif product_name != name:
                    database.update_product(barcode, name)
            self.updateInputOptions()
            self.reloadTable()

            self.epc_list = []
            self.counter_updated.emit(0)
        else:
            QMessageBox.warning(self, "WARNING", "Please enter or scan the product barcode")

    def deleteInbound(self, row):
        barcode = self.table.item(row, 0).text()
        database.delete_inbound(barcode)
        self.updateInputOptions()
        self.reloadTable()

    def reloadTable(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        inbounds = database.get_inbounds()
        for inbound in inbounds:
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(str(inbound[0])))
            self.table.setItem(row_count, 1, QTableWidgetItem(inbound[1]))
            self.table.setItem(row_count, 2, QTableWidgetItem(inbound[2]))
            self.table.setItem(row_count, 3, QTableWidgetItem(str(inbound[3])))
            timestamp = datetime.fromtimestamp(inbound[4] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            self.table.setItem(row_count, 4, QTableWidgetItem(timestamp))
            details_button = QPushButton("Details")
            details_button.setFont(QtGui.QFont("Arial", 12))
            self.table.setCellWidget(row_count, 5, details_button)
            details_button.clicked.connect(lambda state, row=row_count: self.showEpcs(row))
            # delete_button = QPushButton("删除")
            # self.table.setCellWidget(row_count, 6, delete_button)
            # delete_button.clicked.connect(lambda state, row=row_count: self.deleteInbound(row))
        
    def updateInputOptions(self):
        self.barcode_input.clear()
        self.product_name_input.clear()
        barcodes = set()
        names = set()
        products = database.get_products()
        for product in products:
            barcodes.add(product[0])
            names.add(product[1])
        self.barcode_input.addItems(sorted(barcodes))
        self.product_name_input.addItems(sorted(names))
        self.barcode_input.view().setFixedHeight(60 * len(barcodes) + 100) # Add this line to set the height of each item in the barcode input box to 60
        self.product_name_input.view().setFixedHeight(60 * len(names) + 100) # Add this line to set the height of each item in the product name input box to 60                        

    def updateProductName(self, index):
        barcode = self.barcode_input.currentText()
        if barcode:
            name = database.get_product_name(barcode)
            self.product_name_input.setCurrentText(name or '')

    def updateBarcode(self, index):
        name = self.product_name_input.currentText()
        if name:
            barcode = database.get_product_barcode(name)
            if barcode:
                self.barcode_input.setCurrentText(barcode or '')

    def updateCounterThread(self):
        while self.inventoring:
            try:
                time.sleep(1)
                self.counter_updated.emit(len(self.epc_list))
                self.inventory_button.setText(f"STOP[{(str(round(self.inventory_duration_ref[0])) + 's') if self.inventory_duration_ref[0] > 0 else ''}]")
                print(f"Counter updated: {len(self.epc_list)}, inventory_duration_ref: {self.inventory_duration_ref[0]}")
                if not self.counter_thread.is_alive():
                    print("Counter thread terminated.")
                    break
            except Exception as e:
                error_message = str(e)
                print(error_message)
                pass
        print("Counter updated done.")

    def startAsyncInventory(self):
        self.counter_updated.emit(0)
        stop_async_inventory_event.clear()  # Unset the threading.Event object to resume the inventory process
        # self.inventory_button.setEnabled(False)
        self.inventory_button.disconnect()
        self.inventory_button.setText(f"STOP")
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
        quantity = self.counter.value()
        if quantity > 0:
            self.inbound_button.setEnabled(True)
        self.inventory_button.setText("START")
        self.inventory_button.clicked.connect(self.startAsyncInventory)

    def getEpcListThread(self):
        rfid_api.async_get_epc_list(self.epc_list, self.inventory_duration_ref)  # call rfid_api.async_get_epc_list in a new thread
        self.counter_updated.emit(len(self.epc_list))
        self.stopAsyncInventory()

    def startSyncInventory(self):
        self.inventoring = True
        self.epc_list = rfid_api.sync_get_epc_list(self.epc_list)  # call rfid_api.sync_get_epc_list in a new thread        
        self.counter.display(len(self.epc_list))
        print(f"Counter updated: {len(self.epc_list)}")
        self.inventoring = False

    def showEpcs(self, row):
        inbound_id = self.table.item(row, 0).text()
        epcs = database.get_epcs({'inbound_id': inbound_id})
        if not epcs:
            QMessageBox.warning(self, "WARNING", "Epc not found !")
            return
        epc_list_widget = QWidget()
        epc_list_widget.setWindowTitle(f"Epc list of the inbound record {inbound_id}")
        epc_list_widget_layout = QVBoxLayout()
        epc_list_table = QTableWidget()
        epc_list_table.setColumnCount(4)
        epc_list_table.setHorizontalHeaderLabels(["EPC", "Barcode", "Product Name", "Time"])
        for i, data in enumerate(epcs):
            if data:
                epc_item = QTableWidgetItem(data[0])
                barcode_item = QTableWidgetItem(data[1])
                name_item = QTableWidgetItem(data[2])
                timestamp_item = QTableWidgetItem(datetime.fromtimestamp(data[3] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
                epc_list_table.insertRow(i)
                epc_list_table.setItem(i, 0, epc_item)
                epc_list_table.setItem(i, 1, barcode_item)
                epc_list_table.setItem(i, 2, name_item)
                epc_list_table.setItem(i, 3, timestamp_item)
        epc_list_table.resizeColumnsToContents()
        epc_list_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        epc_list_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        epc_list_table.setSelectionMode(QAbstractItemView.SingleSelection)
        epc_list_table.setSortingEnabled(True)
        epc_list_table.doubleClicked.connect(lambda: epc_list_widget.close())
        epc_list_widget_layout.addWidget(epc_list_table)
        epc_list_widget.setLayout(epc_list_widget_layout)
        # Maximize the widget
        epc_list_widget.showMaximized()
        # Set the widget to full screen
        # epc_list_widget.showFullScreen()
        # Set the table width to fill the widget
        epc_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)