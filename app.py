import sys
import os

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QLabel, QLineEdit, QPushButton, QDialog, QMessageBox, QDesktopWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
import qdarktheme

from in_storage import InStorage
from out_storage import OutStorage
from system_config import SystemConfig
from products import Products
from lic import get_mac_address
from lic_encrypt import generate_license, generate_license_file
from lic_decrypt import verify_license
from config import DATA_PATH

# import the resource module
import icon_rc

# 使用QDialog子类，作为前置页面的对话框
class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Enter License')
        self.setFixedWidth(800)
        # 获取当前设备的MAC地址
        mac_address = get_mac_address()
        # 创建一个QLabel显示MAC地址
        self.mac_label = QLabel(f"Your MAC address is: {mac_address}")
        self.mac_label.setFont(QtGui.QFont("Arial", 16))
        self.mac_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # 创建一个QLineEdit输入license
        self.license_edit = QLineEdit()
        self.license_edit.setPlaceholderText("Please enter your license")
        self.license_edit.setFont(QtGui.QFont("Arial", 16))
        # 创建一个QPushButton确认验证
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setFont(QtGui.QFont("Arial", 16))
        self.confirm_button.clicked.connect(self.confirm) # 连接槽函数

        # 设置布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.mac_label)
        vbox.addWidget(self.license_edit)
        vbox.addWidget(self.confirm_button)
        self.setLayout(vbox)

        self.centerOnScreen()

    def confirm(self):
        # 获取输入的license
        license = self.license_edit.text()
        # 验证license是否正确，这里假设正确的license是"123456"
        if license == generate_license():
            generate_license_file(license)
            # 关闭对话框并显示主窗口
            self.accept()
            self.parent().show()
        else:
            # 提示输入错误
            self.license_edit.setText("")
            self.license_edit.setPlaceholderText("Invalid license, please try again")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
             sys.exit()
        else:
            event.ignore()

    def centerOnScreen(self):
        # Get the screen available geometry
        screen_geometry = QDesktopWidget().availableGeometry()
        # Calculate the center point of the screen
        screen_center = screen_geometry.center()
        # Get the dialog geometry
        dialog_geometry = self.frameGeometry()
        # Move the dialog geometry to the center point of the screen
        dialog_geometry.moveCenter(screen_center)
        # Move the dialog to the top-left point of the dialog geometry
        self.move(dialog_geometry.topLeft())
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GreenElement RFID WMS 1.0")
        # create a QIcon object with the resource path
        icon = QIcon(":/icon.png")
        # set the window icon
        self.setWindowIcon(icon) 
        # Create a menu list on the left
        self.menu_list = QListWidget()
        # Set the menu width to 20% of the window width
        self.menu_list.setFixedWidth(100)
        self.menu_list.setMinimumHeight(40 * self.menu_list.count())
        menu_item1 = QListWidgetItem("Inbound")
        menu_item1.setSizeHint(QSize(0, 40))
        menu_item1.setTextAlignment(Qt.AlignHCenter) # Add this line to center the text
        menu_item1.setTextAlignment(Qt.AlignVCenter) # Add this line to center the text vertically
        menu_item2 = QListWidgetItem("Outbound")
        menu_item2.setSizeHint(QSize(0, 40))
        menu_item2.setTextAlignment(Qt.AlignHCenter) # Add this line to center the text
        menu_item2.setTextAlignment(Qt.AlignVCenter) # Add this line to center the text vertically
        menu_item3 = QListWidgetItem("Config")
        menu_item3.setSizeHint(QSize(0, 40))
        menu_item3.setTextAlignment(Qt.AlignHCenter) # Add this line to center the text
        menu_item3.setTextAlignment(Qt.AlignVCenter) # Add this line to center the text vertically
        menu_item4 = QListWidgetItem("Product")
        menu_item4.setSizeHint(QSize(0, 40))
        menu_item4.setTextAlignment(Qt.AlignHCenter) # Add this line to center the text
        menu_item4.setTextAlignment(Qt.AlignVCenter) # Add this line to center the text vertically
        self.menu_list.addItem(menu_item1)
        self.menu_list.addItem(menu_item2)
        self.menu_list.addItem(menu_item4)
        self.menu_list.addItem(menu_item3)
        self.menu_list.setCurrentItem(menu_item1)
        
        # Create a stacked widget on the right to hold different subpages
        self.sub_page = QStackedWidget()
        # Create three subpages and add them to the stacked widget
        self.page1 = InStorage()
        self.page2 = OutStorage()
        self.page3 = SystemConfig()
        self.page4 = Products()
        self.sub_page.addWidget(self.page1)
        self.sub_page.addWidget(self.page2)
        self.sub_page.addWidget(self.page4)
        self.sub_page.addWidget(self.page3)
        # Connect the menu item change signal to the slot function that changes the subpage
        self.menu_list.currentItemChanged.connect(self.changePage)

        # 添加一个属性self.license_dialog，用于保存前置页面的实例，并在initUI方法中创建它。
        # 设置对话框为模态，并设置父窗口为主窗口。
        self.license_dialog = LicenseDialog(self)
        self.license_dialog.setModal(True)

        # Set the main layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.menu_list)
        hbox.addWidget(self.sub_page)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # Set the window size to 1920x1080
        # self.resize(1920, 1080)
        # # Center the window on the screen
        # self.centerOnScreen() 
        self.showMaximized()
        # Set the window to full screen
        # self.showFullScreen()

    # Change the subpage according to the menu item text
    def changePage(self, current, previous):
        if current.text() == "Inbound":
            # Set the current widget of the stacked widget to page1
            # self.sub_page.setCurrentWidget(self.page1)
            self.resetPage1()
        elif current.text() == "Outbound":
            # Set the current widget of the stacked widget to page2
            self.sub_page.setCurrentWidget(self.page2)
        elif current.text() == "Product":
            # Set the current widget of the stacked widget to page3
            self.sub_page.setCurrentWidget(self.page4)
        elif current.text() == "Config":
            # Set the current widget of the stacked widget to page3
            self.sub_page.setCurrentWidget(self.page3)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()      

    # def centerOnScreen(self):
    #     # Get the screen resolution
    #     screen_resolution = QApplication.desktop().screenGeometry()
    #     # Calculate the center point of the screen
    #     center_x = screen_resolution.width() / 2
    #     center_y = screen_resolution.height() / 2
    #     # Calculate the top-left point of the window
    #     top_left_x = center_x - (self.frameSize().width() / 2)
    #     top_left_y = center_y - (self.frameSize().height() / 2)
    #     # Set the window position
    #     self.move(int(top_left_x), int(top_left_y))

    # 重写showEvent方法，在显示主窗口之前，先检查本地是否有缓存的license，如果有则验证是否有效，如果无效或没有缓存，则显示前置页面。
    def showEvent(self, event):
        try:
            if verify_license():
                super().showEvent(event) 
            else:
                raise Exception("Invalid license")
        except Exception as e:
            print(f'Error: {e}')
            # 显示前置页面对话框，并隐藏主窗口。
            if not self.license_dialog.exec_():
                self.hide()

    # 定义一个resetPage1方法，用于删除page1的所有子控件，并重新创建一个新的InStorage实例作为page1。
    def resetPage1(self):
        layout = self.page1.layout()
        for i in reversed(range(layout.count())): 
            item = layout.takeAt(i).widget()
            if item is not None:
                item.deleteLater()
        layout.deleteLater()
        del layout

        index = self.sub_page.indexOf(self.page1)
        del self.page1

        self.page1 = InStorage()
        self.page1.setObjectName("page1")
        self.page1.setProperty("index", index)

        self.sub_page.addWidget(self.page1)
        self.sub_page.setCurrentWidget(self.page1)

def checkDataDir():
    if not os.path.exists(DATA_PATH): # 如果文件夹不存在
        os.makedirs(DATA_PATH) # 创建文件夹
        print("创建了文件夹：", DATA_PATH) # 打印提示信息
    else: # 如果文件夹已存在
        print(DATA_PATH, "文件夹已存在。") # 打印提示信息


if __name__ == '__main__':
    checkDataDir()
    # enable_hi_dpi() must be called before the instantiation of QApplication.
    qdarktheme.enable_hi_dpi()
    app = QApplication([])
    # Apply the complete dark theme to your Qt App.
    # qdarktheme.setup_theme()
    qdarktheme.setup_theme("auto")
    # qdarktheme.setup_theme("light")

    # Customize accent color. https://pyqtdarktheme.readthedocs.io/en/latest/reference/theme_color.html
    # qdarktheme.setup_theme(custom_colors={"primary": "#D0BCFF"})

    # Default is "rounded".
    # stylesheet = qdarktheme.setup_theme(corner_shape="sharp")

    # You can also only load QPalette and stylesheet. qdarktheme.setup_theme uses the following functions internally.
    # palette = qdarktheme.load_palette(theme="dark")
    # stylesheet = qdarktheme.load_stylesheet(theme="dark")

    win = MainWindow()
    win.show()
    app.exec_()
