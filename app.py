from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget
from in_storage import InStorage
from out_storage import OutStorage
from system_config import SystemConfig

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Warehouse Management System")

        # Set the window to full screen
        self.showMaximized()

        # Create a menu list on the left
        self.menu_list = QListWidget()

        # Set the menu width to 20% of the window width
        # Convert the float value to int to avoid error
        self.menu_list.setFixedWidth(int(self.width() * 0.3))

        menu_item1 = QListWidgetItem("入库管理")
        menu_item2 = QListWidgetItem("出库管理")
        menu_item3 = QListWidgetItem("系统配置")
        self.menu_list.addItem(menu_item1)
        self.menu_list.addItem(menu_item2)
        self.menu_list.addItem(menu_item3)

        # Create a stacked widget on the right to hold different subpages
        self.sub_page = QStackedWidget()

        # Create three subpages and add them to the stacked widget
        self.page1 = InStorage()
        self.page2 = OutStorage()
        self.page3 = SystemConfig()

        self.sub_page.addWidget(self.page1)
        self.sub_page.addWidget(self.page2)
        self.sub_page.addWidget(self.page3)

        # Connect the menu item change signal to the slot function that changes the subpage
        self.menu_list.currentItemChanged.connect(self.changePage)

        # Set the main layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.menu_list)
        hbox.addWidget(self.sub_page)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    # Change the subpage according to the menu item text
    def changePage(self, current, previous):
        if current.text() == "入库管理":
            # Set the current widget of the stacked widget to page1
            self.sub_page.setCurrentWidget(self.page1)
        elif current.text() == "出库管理":
            # Set the current widget of the stacked widget to page2
            self.sub_page.setCurrentWidget(self.page2)
        elif current.text() == "系统配置":
            # Set the current widget of the stacked widget to page3
            self.sub_page.setCurrentWidget(self.page3)


if __name__ == '__main__':
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
