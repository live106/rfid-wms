from PyQt5.QtWidgets import QLabel, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

class SystemConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a subpage for 系统配置
        self.label = QLabel("这是系统配置页面")

        # Create a table widget to display some data
        self.table = QTableWidget(5,

        3)
        self.table.setHorizontalHeaderLabels(["参数名称",
        "参数值",
        "备注"])
        self.table.setItem(0,
        0,
        QTableWidgetItem("数据库地址"))
        self.table.setItem(0,
        1,
        QTableWidgetItem("localhost"))
        self.table.setItem(0,
        2,
        QTableWidgetItem(""))
        self.table.setItem(1,
        0,
        QTableWidgetItem("数据库端口"))
        self.table.setItem(1,
        1,
        QTableWidgetItem("3306"))
        self.table.setItem(1,
        2,
        QTableWidgetItem(""))
        self.table.setItem(2,
        0,
        QTableWidgetItem("数据库用户名"))
        self.table.setItem(2,
        1,
        QTableWidgetItem("root"))
        self.table.setItem(2,
        2,
        QTableWidgetItem(""))

        # Set the password item to be hidden by default
        password_item = QTableWidgetItem()
        password_item.setFlags(password_item.flags() ^ Qt.ItemIsEditable)
        password_item.setText("***")
        password_item.setToolTip('双击显示密码')
        password_item.setData(Qt.UserRole,'123456')
        password_item.setTextAlignment(Qt.AlignCenter)

        # Add the password item to the table
        self.table.setItem(
            3,

            1,

            password_item

        )

        # Connect the cell double click signal to the slot function that toggles the password visibility
        self.table.cellDoubleClicked.connect(self.togglePassword)

        # Create a button to perform some action
        self.button = QPushButton("保存")

        # Connect the button click signal to the slot function that shows a message
        self.button.clicked.connect(self.showMessage)

        # Set the subpage layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.table)
        vbox.addWidget(self.button)
        self.setLayout(vbox)

    # Toggle the password visibility when the cell is double clicked
    def togglePassword(self,row,column):
        if row == 3 and column == 1:
            
            # Get the password item from the table
            password_item = self.table.item(row,column)
            
            # If the password is hidden, show it and change the tooltip text
            if password_item.text != '***':
                password_item.setText(password_item.data(Qt.UserRole))
                password_item.setToolTip('双击隐藏密码')
            
            # If the password is shown, hide it and change the tooltip text
            else:
                password_item.setText('***')
                password_item.setToolTip('双击显示密码')

    # Show a message when the button is clicked
    def showMessage(self):
        QMessageBox.information(self,"提示","保存成功！")
