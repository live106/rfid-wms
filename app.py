from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget
from PyQt5.QtCore import Qt, QSize
from in_storage import InStorage
from out_storage import OutStorage
from system_config import SystemConfig
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Warehouse Management System")
        # Set the window size to 1920x1080
        # self.resize(1920, 1080)
        # # Center the window on the screen
        # self.centerOnScreen()      
        self.showMaximized()
        # Set the window to full screen
        # self.showFullScreen()
        # Create a menu list on the left
        self.menu_list = QListWidget()
        # Set the menu width to 20% of the window width
        self.menu_list.setFixedWidth(int(self.width() * 0.2))
        self.menu_list.setMinimumHeight(60 * self.menu_list.count())
        menu_item1 = QListWidgetItem("入库管理")
        menu_item1.setSizeHint(QSize(0, 60))
        menu_item1.setTextAlignment(Qt.AlignHCenter) # Add this line to center the text
        menu_item1.setTextAlignment(Qt.AlignVCenter) # Add this line to center the text vertically
        menu_item2 = QListWidgetItem("出库管理")
        menu_item2.setSizeHint(QSize(0, 60))
        menu_item2.setTextAlignment(Qt.AlignHCenter) # Add this line to center the text
        menu_item2.setTextAlignment(Qt.AlignVCenter) # Add this line to center the text vertically
        menu_item3 = QListWidgetItem("系统配置")
        menu_item3.setSizeHint(QSize(0, 60))
        menu_item3.setTextAlignment(Qt.AlignHCenter) # Add this line to center the text
        menu_item3.setTextAlignment(Qt.AlignVCenter) # Add this line to center the text vertically
        self.menu_list.addItem(menu_item1)
        self.menu_list.addItem(menu_item2)
        self.menu_list.addItem(menu_item3)
        self.menu_list.setCurrentItem(menu_item1)
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()

    def centerOnScreen(self):
        # Get the screen resolution
        screen_resolution = QApplication.desktop().screenGeometry()
        # Calculate the center point of the screen
        center_x = screen_resolution.width() / 2
        center_y = screen_resolution.height() / 2
        # Calculate the top-left point of the window
        top_left_x = center_x - (self.frameSize().width() / 2)
        top_left_y = center_y - (self.frameSize().height() / 2)
        # Set the window position
        self.move(int(top_left_x), int(top_left_y))

    def showEvent(self, event):
        # Call the centerOnScreen method when the window is shown
        self.centerOnScreen()            
            
if __name__ == '__main__':
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()