from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLCDNumber, QHBoxLayout, QHeaderView
from PyQt5.QtCore import Qt
import database
import random
import time
from datetime import datetime

class InStorage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a subpage for 入库管理
        self.label = QLabel("这是入库管理页面")
        
        # Create a table widget to display some data
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["条形码", "商品名称", "数量", "入库时间", "操作"])
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(30)

        # Create a barcode input widget
        self.barcode_input = QComboBox(self)
        self.barcode_input.setEditable(True)
        self.barcode_input.setPlaceholderText("请输入条形码")

        # Create a product name input widget
        self.product_name_input = QComboBox(self)
        self.product_name_input.setEditable(True)
        self.product_name_input.setPlaceholderText("请输入商品名称")

        # Create a text counter to show the number of characters in the product name input box
        self.counter = QLCDNumber()

        # Create a button to perform some action
        self.button = QPushButton("入库")
        self.button.clicked.connect(self.addInbound)

        # Set the subpage layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)

        # Create a horizontal layout to hold the product name input box, the barcode input box, the counter, and the button
        hbox = QHBoxLayout()

        # Add the product name input widget and the barcode input widget to the horizontal layout
        hbox.addWidget(self.barcode_input, 1)
        hbox.addWidget(self.product_name_input, 1)

        # Add the counter and the button to the horizontal layout
        hbox.addWidget(self.counter, 1)
        hbox.addWidget(self.button, 1)

        # Add the horizontal layout to the vertical layout
        vbox.addLayout(hbox)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

        # Call the create_table function from database module to create a table if it does not exist 
        database.create_table()

        # Call the delete_old_data function from database module to delete data that are older than 2 days 
        database.delete_old_data()

        self.initInputs()
        self.initTable()

    def updateCounter(self):
        self.counter.display(len(self.product_name_input.currentText()))

    def addInbound(self):
        barcode = self.barcode_input.currentText()
        name = self.product_name_input.currentText()
        quantity = str(random.randint(1, 10))
        timestamp = int(round(time.time()))
        if barcode:
            database.add_inbound(barcode, name, quantity, timestamp)
            if name:
                # Check if the product exists in the "products" table
                product_name = database.get_product_name(barcode)
                # If the product does not exist, add it to the "products" table
                if not product_name:
                    database.add_product(barcode, name)
                # If the product name does not match current name, update the "products" table
                elif product_name != name:
                    database.update_product(barcode, name)
            self.initInputs()
            self.initTable()
        else:
            QMessageBox.warning(self, "警告", "请扫描或输入商品条形码！")

    def deleteInbound(self, row):
        barcode = self.table.item(row, 0).text()
        database.delete_inbound(barcode)
        self.initInputs()
        self.initTable()

    def initTable(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        inbounds = database.get_inbounds()
        for inbound in inbounds:
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(inbound[0]))
            self.table.setItem(row_count, 1, QTableWidgetItem(inbound[1]))
            self.table.setItem(row_count, 2, QTableWidgetItem(str(inbound[2])))
            timestamp = datetime.fromtimestamp(inbound[3] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            self.table.setItem(row_count, 3, QTableWidgetItem(timestamp))
            self.table.setCellWidget(row_count, 4, QPushButton("删除"))
            self.table.cellWidget(row_count, 4).clicked.connect(lambda state, row=row_count: self.deleteInbound(row))       
        
    def initInputs(self):
        self.barcode_input.clear()
        self.product_name_input.clear()
        barcodes = set()
        names = set()
        products = database.get_products()
        for product in products:
            barcodes.add(product[0])
            names.add(product[1])
        self.barcode_input.setFixedHeight(60) # Add this line to set the height of the barcode input box to 60
        self.product_name_input.setFixedHeight(60) # Add this line to set the height of the product name input box to 60
        self.barcode_input.view().setFixedHeight(60) # Add this line to set the height of each item in the barcode input box to 60
        self.product_name_input.view().setFixedHeight(60) # Add this line to set the height of each item in the product name input box to 60         
        self.barcode_input.addItems(sorted(barcodes))
        self.product_name_input.addItems(sorted(names))               
        self.barcode_input.currentIndexChanged.connect(self.updateProductName)          
        self.barcode_input.currentTextChanged.connect(self.updateProductName)          
        self.product_name_input.currentIndexChanged.connect(self.updateBarcode)
        self.product_name_input.currentTextChanged.connect(self.updateBarcode)

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
