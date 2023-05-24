from PyQt5.QtWidgets import QLabel, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QGridLayout, QDialog, QFrame, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import database # 导入database模块
class SystemConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.title = QLabel('Express Config') # 创建一个标签对象
        self.title.setAlignment(Qt.AlignCenter) # 设置标签居中对齐
        self.title.setFont(QtGui.QFont('Arial', 16)) # 设置标签的字体和大小

        # 创建一个表格控件，显示express_config表中的所有记录
        self.table = QTableWidget()
        self.table.setColumnCount(8) # 设置表格列数为8
        self.table.setHorizontalHeaderLabels(['名称', '用户名', '密码', '用户名字段名', '密码字段名', '登录网址', '登录元素类', '主页网址']) # 设置表格水平表头标签
        self.table.setEditTriggers(QTableWidget.DoubleClicked) # 设置表格双击可编辑
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # 设置表格选择行为为选择整行
        self.table.setSelectionMode(QTableWidget.SingleSelection) # 设置表格选择模式为单选
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 创建三个按钮控件，分别用于添加、删除和更新express_config表中的记录
        self.add_btn = QPushButton('添加')
        self.add_btn.setFont(QtGui.QFont("Arial", 16))
        self.delete_btn = QPushButton('删除')
        self.delete_btn.setFont(QtGui.QFont("Arial", 16))
        # self.update_btn = QPushButton('更新')

        self.separator = QFrame() # 创建一个分隔符对象
        self.separator.setFrameShape(QFrame.HLine) # 设置分隔符的形状为水平线
        self.separator.setFrameShadow(QFrame.Sunken) # 设置分隔符的阴影为凹陷        

        # 创建一个布局控件，将表格控件和按钮控件放在合适的位置
        self.vbox = QVBoxLayout() # 创建一个垂直布局
        self.hbox = QHBoxLayout() # 创建一个水平布局

        self.hbox.addWidget(self.add_btn) # 将添加按钮添加到水平布局中
        self.hbox.addWidget(self.delete_btn) # 将删除按钮添加到水平布局中
        # self.hbox.addWidget(self.update_btn) # 将更新按钮添加到水平布局中

        self.vbox.addWidget(self.title) # 将标签添加到垂直布局中
        self.vbox.addLayout(self.hbox) # 将水平布局添加到垂直布局中
        self.vbox.addWidget(self.table) # 将表格控件添加到垂直布局中
        self.vbox.addWidget(self.separator) # 将分隔符添加到垂直布局中
        self.setLayout(self.vbox) # 将垂直布局设置为窗口的布局

        # 连接按钮的点击信号和相应的槽函数
        self.add_btn.clicked.connect(self.show_add_dialog)
        self.delete_btn.clicked.connect(self.delete_record)
        # self.update_btn.clicked.connect(self.update_record)

        # 初始化默认查询express_config数据填充到列表显示
        self.query_record()

    def show_add_dialog(self):
        # 定义一个显示添加对话框的槽函数，创建一个对话框，包含8个标签和8个输入框，以及一个确定按钮和一个取消按钮，点击确定按钮后调用add_record函数实现数据插入
        self.dialog = QDialog() # 创建一个对话框对象
        self.dialog.setWindowTitle('添加记录') # 设置对话框标题
        self.dialog.setFixedWidth(600) # 设置对话框的固定宽度为600

        # 创建八个标签控件，用于显示快递公司的信息的字段名，并在文字后面增加全角冒号，右对齐
        self.name_label = QLabel('名称：')
        self.name_label.setAlignment(Qt.AlignRight)
        self.username_label = QLabel('用户名：')
        self.username_label.setAlignment(Qt.AlignRight)
        self.password_label = QLabel('密码：')
        self.password_label.setAlignment(Qt.AlignRight)
        self.username_field_name_label = QLabel('用户名字段名：')
        self.username_field_name_label.setAlignment(Qt.AlignRight)
        self.password_field_name_label = QLabel('密码字段名：')
        self.password_field_name_label.setAlignment(Qt.AlignRight)
        self.login_url_label = QLabel('登录网址：')
        self.login_url_label.setAlignment(Qt.AlignRight)
        self.logged_in_element_class_label = QLabel('登录元素类：')
        self.logged_in_element_class_label.setAlignment(Qt.AlignRight)
        self.home_url_label = QLabel('主页网址：')
        self.home_url_label.setAlignment(Qt.AlignRight)

        # 创建八个输入框控件，用于输入快递公司的信息，并设置占位符文本
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('请输入快递公司名称')
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('请输入用户名')
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('请输入密码')
        self.username_field_name_edit = QLineEdit()
        self.username_field_name_edit.setPlaceholderText('请输入用户名字段名')
        self.password_field_name_edit = QLineEdit()
        self.password_field_name_edit.setPlaceholderText('请输入密码字段名')
        self.login_url_edit = QLineEdit()
        self.login_url_edit.setPlaceholderText('请输入登录网址')
        self.logged_in_element_class_edit = QLineEdit()
        self.logged_in_element_class_edit.setPlaceholderText('请输入登录元素类')
        self.home_url_edit = QLineEdit()
        self.home_url_edit.setPlaceholderText('请输入主页网址')

        # 创建两个按钮控件，分别用于确定和取消
        self.ok_btn = QPushButton('确定')
        self.cancel_btn = QPushButton('取消')

        # 创建一个布局控件，将标签控件、输入框控件和按钮控件放在合适的位置
        self.grid = QGridLayout() # 创建一个网格布局
        self.grid.addWidget(self.name_label, 0, 0) # 将名称标签添加到网格布局中
        self.grid.addWidget(self.name_edit, 0, 1) # 将名称输入框添加到网格布局中
        self.grid.addWidget(self.username_label, 1, 0) # 将用户名标签添加到网格布局中
        self.grid.addWidget(self.username_edit, 1, 1) # 将用户名输入框添加到网格布局中
        self.grid.addWidget(self.password_label, 2, 0) # 将密码标签添加到网格布局中
        self.grid.addWidget(self.password_edit, 2, 1) # 将密码输入框添加到网格布局中
        self.grid.addWidget(self.username_field_name_label, 3, 0) # 将用户名字段名标签添加到网格布局中
        self.grid.addWidget(self.username_field_name_edit, 3, 1) # 将用户名字段名输入框添加到网格布局中
        self.grid.addWidget(self.password_field_name_label, 4, 0) # 将密码字段名标签添加到网格布局中
        self.grid.addWidget(self.password_field_name_edit, 4, 1) # 将密码字段名输入框添加到网格布局中
        self.grid.addWidget(self.login_url_label, 5, 0) # 将登录网址标签添加到网格布局中
        self.grid.addWidget(self.login_url_edit, 5, 1) # 将登录网址输入框添加到网格布局中
        self.grid.addWidget(self.logged_in_element_class_label, 6, 0) # 将登录元素类标签添加到网格布局中
        self.grid.addWidget(self.logged_in_element_class_edit, 6, 1) # 将登录元素类输入框添加到网格布局中
        self.grid.addWidget(self.home_url_label, 7, 0) # 将主页网址标签添加到网格布局中
        self.grid.addWidget(self.home_url_edit, 7, 1) # 将主页网址输入框添加到网格布局中
        self.hbox = QHBoxLayout() # 创建一个水平布局
        self.hbox.addStretch(1) # 添加一个弹性空间，使按钮靠右对齐
        self.hbox.addWidget(self.ok_btn) # 将确定按钮添加到水平布局中
        self.hbox.addWidget(self.cancel_btn) # 将取消按钮添加到水平布局中
        self.vbox = QVBoxLayout() # 创建一个垂直布局
        self.vbox.addLayout(self.grid) # 将网格布局添加到垂直布局中
        self.vbox.addLayout(self.hbox) # 将水平布局添加到垂直布局中
        self.dialog.setLayout(self.vbox) # 将垂直布局设置为对话框的布局

        # 连接按钮的点击信号和相应的槽函数
        self.ok_btn.clicked.connect(self.add_record)
        self.cancel_btn.clicked.connect(self.dialog.close)

        # 显示对话框
        self.dialog.show()        

    def add_record(self):
        # 定义一个添加记录的槽函数，获取输入框中的内容，调用database模块的add_express_config函数，向数据库中插入一条记录，然后关闭对话框并刷新表格控件

        # 获取输入框中的内容，如果有空值，则弹出警告信息并返回
        name = self.name_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        username_field_name = self.username_field_name_edit.text()
        password_field_name = self.password_field_name_edit.text()
        login_url = self.login_url_edit.text()
        logged_in_element_class = self.logged_in_element_class_edit.text()
        home_url = self.home_url_edit.text()
        if not (name and username and password and username_field_name and password_field_name and login_url and logged_in_element_class and home_url):
            QMessageBox.warning(self.dialog, '警告', '请填写完整信息！')
            return

        # 调用database模块的add_express_config函数，向数据库中插入一条记录，如果成功，则弹出提示信息，否则弹出错误信息
        try:
            database.add_express_config(name, username, password,
                                        username_field_name,
                                        password_field_name,
                                        login_url,
                                        logged_in_element_class,
                                        home_url)
            QMessageBox.information(self.dialog, '提示', '添加成功！')
        except Exception as e:
            QMessageBox.critical(self.dialog, '错误', str(e))

        # 关闭对话框并刷新表格控件
        self.dialog.close()
        self.query_record()

    def delete_record(self):
        # 定义一个删除记录的槽函数，获取当前选中的行号，然后根据行号获取快递公司的名称，然后调用database模块的delete_express_config函数，从数据库中删除一条记录，最后刷新表格显示和清空输入框内容
        row = self.table.currentRow() # 获取当前选中的行号
        if row != -1: # 如果有选中行
            name = self.table.item(row, 0).text() # 根据行号获取快递公司的名称
            reply = QMessageBox.question(self, '删除记录', f'确定要删除{name}吗？', QMessageBox.Yes | QMessageBox.No) # 弹出确认框
            if reply == QMessageBox.Yes: # 如果用户点击了是
                database.delete_express_config(name) # 调用database模块的delete_express_config函数，从数据库中删除一条记录
                QMessageBox.information(self, '提示', '删除成功！') # 弹出提示信息
            else:
                QMessageBox.warning(self, '警告', '没有选中任何记录！') # 弹出警告信息

            self.query_record() # 刷新表格显示

    def query_record(self):
        # 定义一个查询记录的槽函数，调用database模块的get_all_express_configs函数，查询数据库中的所有记录，然后将结果填充到表格控件中
        self.table.clearContents() # 清空表格内容
        configs = database.get_all_express_configs() # 调用database模块的get_all_express_configs函数，查询数据库中的所有记录
        self.table.setRowCount(len(configs)) # 设置表格行数为查询结果的长度
        for i in range(len(configs)): # 遍历查询结果
            config = configs[i] # 获取一条记录
            for j in range(8): # 遍历记录中的每个字段
                item = QTableWidgetItem(str(config[list(config.keys())[j]])) # 创建一个表格项，将字段值转换为字符串
                item.setTextAlignment(Qt.AlignCenter) # 设置表格项居中对齐
                self.table.setItem(i, j, item) # 将表格项添加到表格控件中