from PyQt5.QtWidgets import QLabel, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QGridLayout, QDialog, QFrame, QHeaderView, QComboBox, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

import database
from auto_express import Express

class SystemConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.title = QLabel('Express Config')
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QtGui.QFont('Arial', 16))
        self.title.setFixedHeight(40)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setFixedHeight(200)
        # self.table.setHorizontalHeaderLabels(['Alias', 'Name', 'Username', 'Password', 'Username Field Name', 'Password Field Name', 'Login URL', 'Logged In Element Class', 'Home URL'])
        self.table.setHorizontalHeaderLabels(['Alias', 'Name', 'Username', 'Password'])
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.add_btn = QPushButton('Add')
        self.add_btn.setFont(QtGui.QFont("Arial", 16))
        self.add_btn.clicked.connect(self.show_add_dialog)

        self.edit_btn = QPushButton('Edit')
        self.edit_btn.setFont(QtGui.QFont("Arial", 16))
        self.edit_btn.clicked.connect(self.show_add_dialog)

        self.delete_btn = QPushButton('Delete')
        self.delete_btn.setFont(QtGui.QFont("Arial", 16))
        self.delete_btn.clicked.connect(self.delete_record)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()

        self.hbox.addWidget(self.add_btn)
        self.hbox.addWidget(self.edit_btn)
        self.hbox.addWidget(self.delete_btn)

        self.vbox.addWidget(self.title)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.table)
        self.vbox.addWidget(self.separator)

        ####
        
        self.rfid_reader_title = QLabel('RFID Reader Config')
        self.rfid_reader_title.setAlignment(Qt.AlignCenter)
        self.rfid_reader_title.setFont(QtGui.QFont('Arial', 16))
        self.rfid_reader_title.setFixedHeight(40)

        self.vbox.addWidget(self.separator)

        self.vbox.addWidget(self.rfid_reader_title)

        self.rfid_reader_form_layout = QFormLayout()

        self.address_label = QLabel('Address:')
        self.address_input = QLineEdit()
        self.rfid_reader_form_layout.addRow(self.address_label, self.address_input)

        self.port_label = QLabel('Port:')
        self.port_input = QLineEdit()
        self.rfid_reader_form_layout.addRow(self.port_label, self.port_input)

        self.antennas_label = QLabel('Antennas:')
        self.antennas_input = QLineEdit()
        self.rfid_reader_form_layout.addRow(self.antennas_label, self.antennas_input)

        self.inventory_duration_label = QLabel('Inventory Duration:')
        self.inventory_duration_input = QLineEdit()
        self.rfid_reader_form_layout.addRow(self.inventory_duration_label, self.inventory_duration_input)

        self.inventory_api_retries_label = QLabel('Inventory API Retries:')
        self.inventory_api_retries_input = QLineEdit()
        self.rfid_reader_form_layout.addRow(self.inventory_api_retries_label, self.inventory_api_retries_input)

        self.consecutive_count_label = QLabel('Consecutive Count:')
        self.consecutive_count_input = QLineEdit()
        self.rfid_reader_form_layout.addRow(self.consecutive_count_label, self.consecutive_count_input)

        self.vbox.addLayout(self.rfid_reader_form_layout)

        self.save_btn = QPushButton('Save')
        self.save_btn.setFont(QtGui.QFont("Arial", 16))
        self.save_btn.clicked.connect(self.save_rfid_config)
        self.rfid_reader_form_layout.addRow(self.save_btn)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.vbox.addWidget(self.separator)

        ####
        
        self.shipper_title = QLabel('Default Shipper Config')
        self.shipper_title.setAlignment(Qt.AlignCenter)
        self.shipper_title.setFont(QtGui.QFont('Arial', 16))
        self.shipper_title.setFixedHeight(40)

        self.vbox.addWidget(self.shipper_title)

        self.shipper_form_layout = QFormLayout()

        self.shipper_zip_label = QLabel('Shipper ZIP:')
        self.shipper_zip_input = QLineEdit()
        self.shipper_form_layout.addRow(self.shipper_zip_label, self.shipper_zip_input)

        self.shipper_name_label = QLabel('Shipper Name:')
        self.shipper_name_input = QLineEdit()
        self.shipper_form_layout.addRow(self.shipper_name_label, self.shipper_name_input)

        self.shipper_address_label = QLabel('Shipper Address:')
        self.shipper_address_input = QLineEdit()
        self.shipper_form_layout.addRow(self.shipper_address_label, self.shipper_address_input)

        self.shipper_tel_label = QLabel('Shipper Tel:')
        self.shipper_tel_input = QLineEdit()
        self.shipper_form_layout.addRow(self.shipper_tel_label, self.shipper_tel_input)

        self.vbox.addLayout(self.shipper_form_layout)

        self.save_btn = QPushButton('Save')
        self.save_btn.setFont(QtGui.QFont("Arial", 16))
        self.save_btn.clicked.connect(self.save_shipper_data)
        self.shipper_form_layout.addRow(self.save_btn)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.vbox.addWidget(self.separator)

        self.setLayout(self.vbox)

        self.query_express_record()
        self.query_rfid_record()
        self.query_shipper_record()

    def query_shipper_record(self):
        # 查询shipper数据
        shipper_data = database.get_shipper_data()
        if shipper_data:
            self.shipper_zip_input.setText(shipper_data['ShipperZIP'])
            self.shipper_name_input.setText(shipper_data['ShipperName'])
            self.shipper_address_input.setText(shipper_data['ShipperAddress'])
            self.shipper_tel_input.setText(shipper_data['ShipperTel'])

    def save_shipper_data(self):
        shipper_zip = self.shipper_zip_input.text()
        shipper_name = self.shipper_name_input.text()
        shipper_address = self.shipper_address_input.text()
        shipper_tel = self.shipper_tel_input.text()

        database.update_shipper(shipper_zip, shipper_name, shipper_address, shipper_tel)
        QMessageBox.information(self, 'Success', 'Default Shipper Configuration saved successfully.')

    def query_rfid_record(self):
        config = database.get_rfid_reader_config()
        if config:
            self.port_input.setText(str(config['port']))
            self.antennas_input.setText(config['antennas'])
            self.inventory_duration_input.setText(str(config['inventory_duration']))
            self.inventory_api_retries_input.setText(str(config['inventory_api_retries']))
            self.address_input.setText(config['address'])
            self.consecutive_count_input.setText(str(config['consecutive_count']))

    def save_rfid_config(self):
        # 获取表单中的数据
        port = int(self.port_input.text())
        antennas = self.antennas_input.text()
        inventory_duration = int(self.inventory_duration_input.text())
        inventory_api_retries = int(self.inventory_api_retries_input.text())
        address = self.address_input.text()
        consecutive_count = int(self.consecutive_count_input.text())

        # 更新数据库中的配置信息
        database.update_rfid_reader_config(port, antennas, inventory_duration, inventory_api_retries, address, consecutive_count)

        # 显示保存成功的提示
        QMessageBox.information(self, 'Success', 'RFID Configuration saved successfully.')

    def show_add_dialog(self):
        sender = self.sender()
        icon = QIcon(":/icon.png")
        self.dialog = QDialog()
        self.dialog.setWindowTitle('Add Express Config' if sender.text() == 'Add' else 'Edit Express Config')
        self.dialog.setWindowIcon(icon)
        self.dialog.setFixedWidth(600)

        self.alias_label = QLabel('Alias: ')
        self.alias_label.setAlignment(Qt.AlignRight)
        self.name_label = QLabel('Name: ')
        self.name_label.setAlignment(Qt.AlignRight)
        self.username_label = QLabel('Username: ')
        self.username_label.setAlignment(Qt.AlignRight)
        self.password_label = QLabel('Password: ')
        self.password_label.setAlignment(Qt.AlignRight)
        self.username_field_name_label = QLabel('Username Field Name: ')
        self.username_field_name_label.setAlignment(Qt.AlignRight)
        self.password_field_name_label = QLabel('Password Field Name: ')
        self.password_field_name_label.setAlignment(Qt.AlignRight)
        self.login_url_label = QLabel('Login URL: ')
        self.login_url_label.setAlignment(Qt.AlignRight)
        self.logged_in_element_class_label = QLabel('Logged In Element Class: ')
        self.logged_in_element_class_label.setAlignment(Qt.AlignRight)
        self.home_url_label = QLabel('Home URL: ')
        self.home_url_label.setAlignment(Qt.AlignRight)
        self.download_path_label = QLabel('Download Path: ')
        self.download_path_label.setAlignment(Qt.AlignRight)

        # create eight line edit widgets for entering express company information, and set placeholder text
        self.alias_edit = QLineEdit()
        self.alias_edit.setPlaceholderText('Please enter express alias')

        self.name_edit = QComboBox()
        self.name_edit.setPlaceholderText('Please select express company name')
        # 添加枚举类成员值作为选项
        for express in Express:
            self.name_edit.addItem(express.value)
        self.name_edit.currentIndexChanged.connect(self.handleExpressInputChange)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('Please enter username')
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('Please enter password')
        self.username_field_name_edit = QLineEdit()
        self.username_field_name_edit.setPlaceholderText(
            'Please enter username field name')
        self.password_field_name_edit = QLineEdit()
        self.password_field_name_edit.setPlaceholderText(
            'Please enter password field name')
        self.login_url_edit = QLineEdit()
        self.login_url_edit.setPlaceholderText('Please enter login URL')
        self.logged_in_element_class_edit = QLineEdit()
        self.logged_in_element_class_edit.setPlaceholderText(
            'Please enter logged in element class')
        self.home_url_edit = QLineEdit()
        self.home_url_edit.setPlaceholderText('Please enter home URL')
        self.download_path_edit = QLineEdit()
        self.download_path_edit.setPlaceholderText('Please enter download path')

        # create two button widgets for ok and cancel
        self.ok_btn = QPushButton('Ok')
        self.cancel_btn = QPushButton('Cancel')

        # 设置默认选中的枚举类成员
        self.name_edit.setCurrentText(Express.SAGAWAEXP.value)

        # create a layout widget to place the label widgets, line edit widgets and button widgets in appropriate positions
        self.grid = QGridLayout()  # create a grid layout
        # add the alias label to the grid layout
        self.grid.addWidget(self.alias_label, 0, 0)
        # add the alias line edit to the grid layout
        self.grid.addWidget(self.alias_edit, 0, 1)
        # add the name label to the grid layout
        self.grid.addWidget(self.name_label, 1, 0)
        # add the name line edit to the grid layout
        self.grid.addWidget(self.name_edit, 1, 1)
        # add the username label to the grid layout
        self.grid.addWidget(self.username_label, 2, 0)
        # add the username line edit to the grid layout
        self.grid.addWidget(self.username_edit, 2, 1)
        # add the password label to the grid layout
        self.grid.addWidget(self.password_label, 3, 0)
        # add the password line edit to the grid layout
        self.grid.addWidget(self.password_edit, 3, 1)
        # add the username field name label to the grid layout
        self.grid.addWidget(self.username_field_name_label, 4, 0)
        # add the username field name line edit to the grid layout
        self.grid.addWidget(self.username_field_name_edit, 4, 1)
        # add the password field name label to the grid layout
        self.grid.addWidget(self.password_field_name_label, 5, 0)
        # add the password field name line edit to the grid layout
        self.grid.addWidget(self.password_field_name_edit, 5, 1)
        # add the login URL label to the grid layout
        self.grid.addWidget(self.login_url_label, 6, 0)
        # add the login URL line edit to the grid layout
        self.grid.addWidget(self.login_url_edit, 6, 1)
        # add the logged in element class label to the grid layout
        self.grid.addWidget(self.logged_in_element_class_label, 7, 0)
        # add the logged in element class line edit to the grid layout
        self.grid.addWidget(self.logged_in_element_class_edit, 7, 1)
        # add the home URL label to the grid layout
        self.grid.addWidget(self.home_url_label, 8, 0)
        # add the home URL line edit to the grid layout
        self.grid.addWidget(self.home_url_edit, 8, 1)
        # add the download path label to the grid layout
        self.grid.addWidget(self.download_path_label, 9, 0)
        # add the download path line edit to the grid layout
        self.grid.addWidget(self.download_path_edit, 9, 1)
        self.hbox = QHBoxLayout()  # create a horizontal layout
        # add a stretch space to make buttons right align
        self.hbox.addStretch(1)
        # add the ok button to the horizontal layout
        self.hbox.addWidget(self.ok_btn)
        # add the cancel button to the horizontal layout
        self.hbox.addWidget(self.cancel_btn)
        self.vbox = QVBoxLayout()  # create a vertical layout
        # add the grid layout to the vertical layout
        self.vbox.addLayout(self.grid)
        # add the horizontal layout to the vertical layout
        self.vbox.addLayout(self.hbox)
        # set the vertical layout as the dialog's layout
        self.dialog.setLayout(self.vbox)

        #
        if sender.text() == 'Edit':
            selected_rows = self.table.selectionModel().selectedRows()
            if len(selected_rows) == 0:
                print("No rows selected.")
            else:
                alias = self.table.item(selected_rows[0].row(), 0).text()  # Assuming name is in the second column
                config = database.get_express_config(alias)
                if config:
                    self.alias_edit.setText(config.get('alias', ''))
                    self.name_edit.setCurrentText(config.get('name', ''))
                    self.username_edit.setText(config.get('username', ''))
                    self.password_edit.setText(config.get('password', ''))
                    self.username_field_name_edit.setText(config.get('username_field_name', ''))
                    self.password_field_name_edit.setText(config.get('password_field_name', ''))
                    self.login_url_edit.setText(config.get('login_url', ''))
                    self.logged_in_element_class_edit.setText(config.get('logged_in_element_class', ''))
                    self.home_url_edit.setText(config.get('home_url', ''))
                    self.download_path_edit.setText(config.get('download_path', ''))
                else:
                    print("Config not found for the selected name.")
        else:
            self.table.clearSelection()

        # connect button's clicked signals to corresponding slot functions
        self.ok_btn.clicked.connect(self.add_or_update_express_record)
        self.cancel_btn.clicked.connect(self.dialog.close)

        # show dialog
        self.dialog.show()

    def handleExpressInputChange(self):
        name = self.name_edit.currentText()
        config = database.get_express_config_by_name(name)
        if config:
            self.username_field_name_edit.setText(config.get('username_field_name', ''))
            self.password_field_name_edit.setText(config.get('password_field_name', ''))
            self.login_url_edit.setText(config.get('login_url', ''))
            self.logged_in_element_class_edit.setText(config.get('logged_in_element_class', ''))
            self.home_url_edit.setText(config.get('home_url', ''))
            self.home_url_edit.setText(config.get('home_url', ''))
            self.download_path_edit.setText(config.get('download_path', ''))
            self.download_path_edit.setText(config.get('download_path', ''))


    def add_or_update_express_record(self):
        # define a slot function to add record , get content from line edits , call database module's add_express_config function , insert data into database , then close dialog and refresh table widget

        # get content from line edits , if there is empty value , pop up warning message and return
        alias = self.alias_edit.text()
        name = self.name_edit.currentText()
        username = self.username_edit.text()
        password = self.password_edit.text()
        username_field_name = self.username_field_name_edit.text()
        password_field_name = self.password_field_name_edit.text()
        login_url = self.login_url_edit.text()
        logged_in_element_class = self.logged_in_element_class_edit.text()
        home_url = self.home_url_edit.text()
        download_path = self.download_path_edit.text()
        if not (alias and name and username and password and username_field_name and password_field_name and login_url and logged_in_element_class and home_url):
            QMessageBox.warning(self.dialog, 'Warning', 'Please fill in complete information!')
            return

        last_alias = None
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) > 0:
            last_alias = self.table.item(selected_rows[0].row(), 0).text()
        try:
            if last_alias and database.get_express_config(last_alias):
                database.update_express_config(last_alias, alias, name, username, password,
                                        username_field_name,
                                        password_field_name,
                                        login_url,
                                        logged_in_element_class,
                                        home_url,
                                        download_path)
                QMessageBox.information(self.dialog, 'Info', 'Edit Express Configuration success !')
            else:
                if database.get_express_config(alias):
                    QMessageBox.warning(self.dialog, 'Warning', f'Alias {alias} exists already !')
                    return
                database.add_express_config(alias, name, username, password,
                                        username_field_name,
                                        password_field_name,
                                        login_url,
                                        logged_in_element_class,
                                        home_url,
                                        download_path)
                QMessageBox.information(self.dialog, 'Info', 'Add Express Configuration success !')
        except Exception as e:
            QMessageBox.critical(self.dialog, 'Error', str(e))

        # close dialog and refresh table widget
        self.dialog.close()
        self.query_express_record()

    def delete_record(self):
        # define a slot function to delete record , get current selected row number , then get express company name according to row number , then call database module's delete_express_config function , delete a record from database , finally refresh table display and clear line edit content
        row = self.table.currentRow()  # get current selected row number
        if row != -1:  # if there is selected row
            # get express company name according to row number
            alias = self.table.item(row, 0).text()
            reply = QMessageBox.question(
                self, 'Delete Record', f'Are you sure you want to delete {alias}?', QMessageBox.Yes | QMessageBox.No)  # pop up confirm box
        if reply == QMessageBox.Yes:  # if user clicked yes
            # call database module's delete_express_config function , delete a record from database
            database.delete_express_config(alias)
            # pop up prompt message
            QMessageBox.information(self, 'Prompt', 'Delete success!')
        else:
            # pop up warning message
            QMessageBox.warning(self, 'Warning', 'No record selected!')

        self.query_express_record()  # refresh table widget

    def query_express_record(self):
        self.table.clearContents()
        configs = database.get_all_express_configs()
        self.table.setRowCount(len(configs))
        for i in range(len(configs)):
            config = configs[i]
            for j in range(4):
                item = QTableWidgetItem(str(config[list(config.keys())[j]]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)