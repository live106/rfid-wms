from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, QLCDNumber, QHBoxLayout, QHeaderView, QComboBox
from PyQt5.QtCore import Qt
import database # Import the database module

class InStorage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a subpage for 入库管理
        self.label = QLabel("这是入库管理页面")
        
        # Create a table widget to display some data
        self.table = QTableWidget(0,

4)self.table.setHorizontalHeaderLabels(["条形码",
"商品名称",
"数量",
"操作"])self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)



# Create

a combobox to enter some data

self.input =

QComboBox(

self)



# Set

the combobox to be editable

self.input.setEditable(

True)



# Set

the insert policy of the combobox to insert new values at the end of the list

self.input.setInsertPolicy(

QComboBox.InsertAtBottom)



# Connect

the input text changed signal to the slot function that updates the product name

self.input.editTextChanged.connect(

self.updateProductName)



# Create

a text counter to show the number of characters in the input box

self.counter =

QLCDNumber()



# Connect

the input text changed signal to the slot function that updates the counter

self.input.editTextChanged.connect(

self.updateCounter)



# Create

a label to display the product name

self.product_name =

QLabel()



# Set

the label text alignment to center

self.product_name.setAlignment(

Qt.AlignCenter)



# Set

the label font size to 2 times larger than default

font =

self.product_name.font()

font.setPointSize(

font.pointSize() * 2)

self.product_name.setFont(

font)



# Create

a button to perform some action

self.button =

QPushButton(

"入库")



# Connect

the button click signal to the slot function that adds data to the table and database

self.button.clicked.connect(

self.addData)



# Set

the subpage layout

vbox =

QVBoxLayout()

vbox.addWidget(

self.label)



# Create

a horizontal layout to hold the input box,

the counter,

the product name and the button

hbox =

QHBoxLayout()



# Add

the widgets with equal stretch factors

hbox.addWidget(

self.input,

1)

hbox.addWidget(

self.counter,

1)

hbox.addWidget(

self.product_name,

1)

hbox.addWidget(

self.button,

1)



# Add

the horizontal layout to the vertical layout

vbox.addLayout(

hbox)



vbox.addWidget(

self.table)



self.setLayout(

vbox)



# Call 

the create_table function from database module to create a table if it does not exist 

database.create_table()



# Call 

the delete_old_data function from database module to delete data that are older than 2 days 

database.delete_old_data()



# Update 

the counter when the input text changes 

def updateCounter(self):



# Get 

the length of 

the input text 

length =

len(self.input.currentText())



# Display 

the length on 

the counter 

self.counter.display(length)



# Update 

the product name based on 

the input text 

def updateProductName(self):



# Update 

the product name based on 

the input text 

# For simplicity,

assume that 

the input text is a barcode that can be mapped to a product name 

# In reality,

this could be done by querying a database or an API 

barcode_to_product =

{

"1234567890":

"电脑",

"0987654321":

"手机",

"1357924680":

"平板",

"2468013579":

"耳机",

"8642097531":

"键盘"

}



# If 

the input text matches a barcode,

show the product name on 

the label 

if self.input.currentText() in barcode_to_product:

self.product_name.setText(barcode_to_product[self.input.currentText()])



# If 

the input text does not match a barcode,

clear the label 

else:

self.product_name.setText("")



# Add 

data to 

the table and database when the button is clicked 

def addData(self):



# Get 

the input text and 

the product name 

barcode =

self.input.currentText()

product =

self.product_name.text()



# If both are not empty,

add a new row to 

the table with them and some default values for quantity and operation 

if barcode and product:

# Get the current row count of the table
row_count = self.table.rowCount()

# Insert a new row at the end of the table
self.table.insertRow(row_count)

# Create items for each column and set their text and alignment
barcode_item = QTableWidgetItem(barcode)
barcode_item.setTextAlignment(Qt.AlignCenter)

product_item = QTableWidgetItem(product)
product_item.setTextAlignment(Qt.AlignCenter)

quantity_item = QTableWidgetItem("1")
quantity_item.setTextAlignment(Qt.AlignCenter)

operation_item = QTableWidgetItem("删除")
operation_item.setTextAlignment(Qt.AlignCenter)

# Add the items to the table at the new row
self.table.setItem(row_count, 0, barcode_item)
self.table.setItem(row_count, 1, product_item)
self.table.setItem(row_count, 2, quantity_item)
self.table.setItem(row_count, 3, operation_item)

# Connect the cell click signal to the slot function that deletes data from the table and database
self.table.cellClicked.connect(self.deleteData)

# Call the insert_data function from database module to insert data into the database
database.insert_data(barcode, product, 1)

# Show a message that adding data was successful
QMessageBox.information(self,"提示",f"入库成功！您输入的是：{barcode}")
