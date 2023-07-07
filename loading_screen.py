from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication

class LoadingScreen(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet("color: white; font-size: 48px;")
        self.loading_label.setAlignment(Qt.AlignCenter)

        background_color = QColor(0, 0, 0, 200)
        self.setStyleSheet(f"background-color: {background_color.name()};")

        layout = self.layout()
        layout.addWidget(self.loading_label)

    def update_loading_text(self, text):
        if text:
            self.show_loading_screen()
            self.loading_label.setText(text)
        else:
            self.close_loading_screen()

    def show_loading_screen(self):
        # desktop = QApplication.desktop()
        # screen_rect = desktop.availableGeometry()
        # self.setGeometry(screen_rect)
        # self.show()
        self.showFullScreen()

    def close_loading_screen(self):
        self.close()
