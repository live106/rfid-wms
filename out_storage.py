from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox

class OutStorage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a subpage for 出库管理
        self.label = QLabel("这是出库管理页面")
        
         # Create a table widget to display some data
        self.table = QTableWidget(5,

        3)
        self.table.setHorizontalHeaderLabels(["商品名称",
        "数量",
        "价格"])
        self.table.setItem(0,
        0,
        QTableWidgetItem("电脑"))
        self.table.setItem(0,
        1,
        QTableWidgetItem("10"))
        self.table.setItem(0,
        2,
        QTableWidgetItem("5000"))
        self.table.setItem(1,
        0,
        QTableWidgetItem("手机"))
        self.table.setItem(1,
        1,
        QTableWidgetItem("20"))
        self.table.setItem(1,
        2,
        QTableWidgetItem("3000"))
        # Create a button to perform some action
        self.button = QPushButton(
        "出库")

        # Connect the button click signal to the slot function that shows a message
        self.button.clicked.connect(
        self.showMessage)

        # Set the subpage layout
        vbox = QVBoxLayout()
        vbox.addWidget(
        self.label)

        vbox.addWidget(
        self.button)
        
        vbox.addWidget(
        self.table)


        self.setLayout(
        vbox)

    # Show a message when the button is clicked
    def showMessage(
    self):

        QMessageBox.information(
    self,

    "提示",

    "出库成功！")
