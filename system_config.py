from PyQt5.QtWidgets import QLabel, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QGridLayout, QDialog, QFrame, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import database

from PyQt5.QtGui import QIcon
class SystemConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.title = QLabel('Express Config')
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QtGui.QFont('Arial', 16))

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['Name', 'Username', 'Password', 'Username Field Name', 'Password Field Name', 'Login URL', 'Logged In Element Class', 'Home URL'])
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.add_btn = QPushButton('Add')
        self.add_btn.setFont(QtGui.QFont("Arial", 16))
        self.delete_btn = QPushButton('Delete')
        self.delete_btn.setFont(QtGui.QFont("Arial", 16))

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()

        self.hbox.addWidget(self.add_btn)
        self.hbox.addWidget(self.delete_btn)

        self.vbox.addWidget(self.title)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.table)
        self.vbox.addWidget(self.separator)
        self.setLayout(self.vbox)

        self.add_btn.clicked.connect(self.show_add_dialog)
        self.delete_btn.clicked.connect(self.delete_record)

        self.query_record()

    def show_add_dialog(self):
        icon = QIcon(":/icon.png")
        self.dialog = QDialog()
        self.dialog.setWindowTitle('Add Record')
        self.dialog.setWindowIcon(icon)
        self.dialog.setFixedWidth(600)

        self.name_label = QLabel('Name：')
        self.name_label.setAlignment(Qt.AlignRight)
        self.username_label = QLabel('Username：')
        self.username_label.setAlignment(Qt.AlignRight)
        self.password_label = QLabel('Password：')
        self.password_label.setAlignment(Qt.AlignRight)
        self.username_field_name_label = QLabel('Username Field Name：')
        self.username_field_name_label.setAlignment(Qt.AlignRight)
        self.password_field_name_label = QLabel('Password Field Name：')
        self.password_field_name_label.setAlignment(Qt.AlignRight)
        self.login_url_label = QLabel('Login URL：')
        self.login_url_label.setAlignment(Qt.AlignRight)
        self.logged_in_element_class_label = QLabel('Logged In Element Class：')
        self.logged_in_element_class_label.setAlignment(Qt.AlignRight)
        self.home_url_label = QLabel('Home URL：')
        self.home_url_label.setAlignment(Qt.AlignRight)

        # create eight line edit widgets for entering express company information, and set placeholder text
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Please enter express company name')
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('Please enter username')
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('Please enter password')
        self.username_field_name_edit = QLineEdit()
        self.username_field_name_edit.setPlaceholderText('Please enter username field name')
        self.password_field_name_edit = QLineEdit()
        self.password_field_name_edit.setPlaceholderText('Please enter password field name')
        self.login_url_edit = QLineEdit()
        self.login_url_edit.setPlaceholderText('Please enter login URL')
        self.logged_in_element_class_edit = QLineEdit()
        self.logged_in_element_class_edit.setPlaceholderText('Please enter logged in element class')
        self.home_url_edit = QLineEdit()
        self.home_url_edit.setPlaceholderText('Please enter home URL')

        # create two button widgets for ok and cancel
        self.ok_btn = QPushButton('Ok')
        self.cancel_btn = QPushButton('Cancel')

        # create a layout widget to place the label widgets, line edit widgets and button widgets in appropriate positions
        self.grid = QGridLayout() # create a grid layout
        self.grid.addWidget(self.name_label, 0, 0) # add the name label to the grid layout
        self.grid.addWidget(self.name_edit, 0, 1) # add the name line edit to the grid layout
        self.grid.addWidget(self.username_label, 1, 0) # add the username label to the grid layout
        self.grid.addWidget(self.username_edit, 1, 1) # add the username line edit to the grid layout
        self.grid.addWidget(self.password_label, 2, 0) # add the password label to the grid layout
        self.grid.addWidget(self.password_edit, 2, 1) # add the password line edit to the grid layout
        self.grid.addWidget(self.username_field_name_label, 3, 0) # add the username field name label to the grid layout
        self.grid.addWidget(self.username_field_name_edit, 3, 1) # add the username field name line edit to the grid layout
        self.grid.addWidget(self.password_field_name_label, 4, 0) # add the password field name label to the grid layout
        self.grid.addWidget(self.password_field_name_edit, 4, 1) # add the password field name line edit to the grid layout
        self.grid.addWidget(self.login_url_label, 5, 0) # add the login URL label to the grid layout
        self.grid.addWidget(self.login_url_edit, 5, 1) # add the login URL line edit to the grid layout
        self.grid.addWidget(self.logged_in_element_class_label, 6, 0) # add the logged in element class label to the grid layout
        self.grid.addWidget(self.logged_in_element_class_edit, 6, 1) # add the logged in element class line edit to the grid layout
        self.grid.addWidget(self.home_url_label, 7, 0) # add the home URL label to the grid layout
        self.grid.addWidget(self.home_url_edit, 7, 1) # add the home URL line edit to the grid layout
        self.hbox = QHBoxLayout() # create a horizontal layout
        self.hbox.addStretch(1) # add a stretch space to make buttons right align
        self.hbox.addWidget(self.ok_btn) # add the ok button to the horizontal layout
        self.hbox.addWidget(self.cancel_btn) # add the cancel button to the horizontal layout
        self.vbox = QVBoxLayout() # create a vertical layout
        self.vbox.addLayout(self.grid) # add the grid layout to the vertical layout
        self.vbox.addLayout(self.hbox) # add the horizontal layout to the vertical layout
        self.dialog.setLayout(self.vbox) # set the vertical layout as the dialog's layout

        # connect button's clicked signals to corresponding slot functions
        self.ok_btn.clicked.connect(self.add_record)
        self.cancel_btn.clicked.connect(self.dialog.close)

        # show dialog
        self.dialog.show() 

    def add_record(self):
        # define a slot function to add record , get content from line edits , call database module's add_express_config function , insert data into database , then close dialog and refresh table widget

        # get content from line edits , if there is empty value , pop up warning message and return 
        name = self.name_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        username_field_name = self.username_field_name_edit.text()
        password_field_name = self.password_field_name_edit.text()
        login_url = self.login_url_edit.text()
        logged_in_element_class = self.logged_in_element_class_edit.text()
        home_url = self.home_url_edit.text()
        if not (name and username and password and username_field_name and password_field_name and login_url and logged_in_element_class and home_url):
            QMessageBox.warning(self.dialog,'Warning','Please fill in complete information!')
            return

        # call database module's add_express_config function , insert data into database , if success , pop up prompt message , else pop up error message 
        try:
            database.add_express_config(name , username , password ,
            username_field_name ,
            password_field_name ,
            login_url ,
            logged_in_element_class ,
            home_url )
            QMessageBox.information (self.dialog,'Prompt','Add success!')
        except Exception as e:
            QMessageBox.critical (self.dialog,'Error',str(e))

        # close dialog and refresh table widget 
        self.dialog.close ()
        self.query_record ()

    def delete_record (self):
        # define a slot function to delete record , get current selected row number , then get express company name according to row number , then call database module's delete_express_config function , delete a record from database , finally refresh table display and clear line edit content 
        row=self.table.currentRow ()# get current selected row number 
        if row != -1 :# if there is selected row 
            name=self.table.item (row ,0).text ()# get express company name according to row number 
            reply=QMessageBox.question (self ,'Delete Record' ,f'Are you sure you want to delete {name}?' ,QMessageBox.Yes | QMessageBox.No )# pop up confirm box 
        if reply == QMessageBox.Yes :# if user clicked yes 
            database.delete_express_config (name)# call database module's delete_express_config function , delete a record from database 
            QMessageBox.information (self ,'Prompt' ,'Delete success!')# pop up prompt message 
        else :
            QMessageBox.warning (self ,'Warning' ,'No record selected!')# pop up warning message

        self.query_record() # refresh table widget

    def query_record(self):
        self.table.clearContents()
        configs = database.get_all_express_configs()
        self.table.setRowCount(len(configs))
        for i in range(len(configs)):
            config = configs[i]
            for j in range(8):
                item = QTableWidgetItem(str(config[list(config.keys())[j]]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)