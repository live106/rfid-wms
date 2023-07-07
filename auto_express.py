from PyQt5.QtCore import QObject, pyqtSignal
import abc
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from enum import Enum
import database
import time
import pyautogui
import os
import datetime

from config import ORDER_FOR_EXPRESS_PATH, DOWNLOAD_PATH

class Express(Enum):
    KURONEKOYAMATO = "yamato"
    SAGAWAEXP = "sagawa"

printer_pool = {}

def create_express_printer(alias):
    config = database.get_express_config(alias)
    if not config:
        raise ValueError("no express config for alias: ", alias)
    username = config['username']
    password = config['password']
    username_field_name = config['username_field_name']
    password_field_name = config['password_field_name']
    login_url = config['login_url']
    logged_in_element_class = config['logged_in_element_class']
    home_url = config['home_url']
    download_path = config['download_path']
    name = config['name']
    if printer_pool.get(alias, None):
        return printer_pool.get(alias, None)
    if name == Express.KURONEKOYAMATO.value:
        printer = ExpressPrinterK(username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url)
    elif name == Express.SAGAWAEXP.value:
        printer = ExpressPrinterS(username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path)
    else:
        raise ValueError("no express printer for alias: " + alias + " and name: ", name)
    printer_pool[alias] = printer
    return printer

class ExpressPrinter(QObject):

    update_loading_text = pyqtSignal(str)

    def __init__(self, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path=None):
        super().__init__()

        self.username = username
        self.password = password
        self.username_field_name = username_field_name
        self.password_field_name = password_field_name
        self.login_url = login_url
        self.logged_in_element_class = logged_in_element_class
        self.home_url = home_url
        self.download_path = download_path if download_path else DOWNLOAD_PATH

        self.logged_in = False

        self.options = webdriver.ChromeOptions()
        # set headless mode
        self.options.add_argument("--headless")

        # prevent the driver from automatically closing the browser for debugging
        # self.options.add_experimental_option("detach", True)

        self.options.add_argument('--enable-print-browser')
        '''
        The --kiosk-printing option is used in the provided code to enable printing in kiosk mode. 
        Kiosk mode is a full-screen mode that is commonly used in public places such as airports, museums, and libraries to provide access to information or services. 
        In kiosk mode, the browser is locked down and only allows access to a specific website or application.
        '''
        # self.options.add_argument("--kiosk-printing")
        # options.add_argument("--start-maximized")

        self.options.add_argument("--disable-gpu")  # 禁用GPU加速
        self.options.add_argument("--disable-software-rasterizer")  # 禁用软件光栅化器
        self.options.add_argument("--disable-dev-shm-usage")  # 禁用/dev/shm
        self.options.add_argument("--no-sandbox")  # 禁用沙箱

        # 设置默认下载路径
        self.options.add_experimental_option("prefs", {  
            "download.default_directory": self.download_path, 
            "download.prompt_for_download": False,  
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True 
        })

        self.driver = webdriver.Chrome(options=self.options)

    def input_text(self, element_id, text, message):
        element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, element_id)))
        element.send_keys(text)
        # self.driver.execute_script("arguments[0].value = arguments[1]", element, text)
        self.update_loading_text.emit(f'{message}: {text}')
        return element
    
    def convert_d_time(self, d_time):
        '''
        午前中                  01
        12:00～14:00          12
        14:00～16:00        14
        16:00～18:00          16
        18:00～20:00          18
        19:00～21:00          19
        '''
        print('d_time: ', d_time)
        if not d_time:
            return ''
        if d_time == '01':
            return '午前中'
        if d_time == '12':
            return '12時～14時'
        if d_time == '14':
            return '14時～16時'
        if d_time == '16':
            return '16時～18時'
        if d_time == '18':
            return '18時～20時'
        # if d_time == '18':
        #     return '18時～21時'
        if d_time == '19':
            return '19時～21時'
        return ''

    def print_express_with_file(self):
        pass

    def print_express_with_form(self, orders):
        pass

    def check_download_finish(self):
        # 等待下载完成
        wait_time = 10  # 最大等待时间，单位为秒
        downloaded_files = []

        while wait_time > 0:
            time.sleep(1)
            wait_time -= 1

            # 检查下载文件目标文件夹，判断是否有新的文件下载完成
            files = os.listdir(self.download_path)
            new_files = [file for file in files if file not in downloaded_files]
            if len(new_files) > 0:
                # 检查每个新下载的文件是否稳定
                for file in new_files:
                    if file in downloaded_files:
                        continue
                    file_path = os.path.join(self.download_path, file)
                    file_exists = os.path.isfile(file_path)
                    if not file_exists:
                        continue

                    file_size_prev = os.path.getsize(file_path)

                    # 等待文件大小稳定
                    while True:
                        time.sleep(1)
                        file_exists = os.path.isfile(file_path)
                        if not file_exists:
                            break # 文件已被删除，忽略
                        # 检查文件大小是否还在变化
                        file_size_current = os.path.getsize(file_path)
                        if file_size_current != file_size_prev:
                            file_size_prev = file_size_current
                        else:
                            break  # 文件大小稳定，跳出循环

                    downloaded_files.append(file)
                    print("文件下载完成:", file)
            else:
                break

        if wait_time <= 0:
            print("文件下载超时")

        return downloaded_files
    
    def check_download_finish0(self):
        # 等待下载完成
        wait_time = 10  # 最大等待时间，单位为秒

        while wait_time > 0:
            time.sleep(1)
            wait_time -= 1

            # 检查下载文件目标文件夹，判断是否有新的 .crdownload 文件
            files = os.listdir(self.download_path)
            new_crdownload_files = [
                file for file in files if file.endswith(".crdownload")
            ]

            if len(new_crdownload_files) == 0:
                # 没有.crdownload 文件，下载完成
                break

        if wait_time <= 0:
            print("文件下载超时")
        else:
            print("文件下载完成")

    def print_message(self, text):
        print(text)
        self.update_loading_text.emit(text)
        
class ExpressPrinterK(ExpressPrinter):
    def print_express_with_file(self):
        for i in range(3):
            try:
                self.driver.get(self.login_url)
                logged_in_element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, self.logged_in_element_class)))
                print('Logged in already!')
            except:
                username_field = self.driver.find_element(By.NAME, self.username_field_name)
                password_field = self.driver.find_element(By.NAME, self.password_field_name)
                username_field.send_keys(self.username)
                password_field.send_keys(self.password)
                password_field.send_keys(Keys.RETURN)
                print('Logged in successfully!')
            
            try:
                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//a[@onclick=\"javascript:ybmCommonJs.useService('06', '2');\"]")))
                element.click()
                print('click 送り状発行システムB2クラウド')

                time.sleep(2)
                
                element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'ex_data_import')))
                self.driver.execute_script("window.scrollBy(0, 200)")
                # actions = ActionChains(self.driver)
                # actions.move_to_element(element).click().perform()
                element.click()
                print('click ●外部データから発行')
                
                select_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "torikomi_pattern")))
                actions = ActionChains(self.driver)
                actions.move_to_element(select_element).click().perform()    
                option_element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//option[text()='GET']")))
                option_element.click()
                print('select 取込みパターン: GET')
                
                element = self.driver.execute_script("return document.getElementById('filename');")
                self.driver.execute_script("arguments[0].style.display = 'block';", element)
                element.send_keys(ORDER_FOR_EXPRESS_PATH)    
                print('set upload file')
                
                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.ID, 'import_start')))
                element.click()
                print('click 取込み開始')
                
                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'allCheck')))
                status = element.get_attribute('checked')
                print('status:', status)
                if not status:
                    element.click()
                    print('click 選択')
                
                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, 'confirm_issue_btn2')))
                element.click()
                print('click 印刷内容の確認へ')

                time.sleep(3)
                
                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, 'start_print')))
                element.click()
                print('click 発行開始')

                time.sleep(5)

                # Switch to the iframe that contains the PDF
                iframe = self.driver.find_element(By.XPATH, "//iframe[@class='fancybox-iframe']")
                self.driver.switch_to.frame(iframe)

                # self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'p')

                self.driver.execute_script("window.print();")

                time.sleep(1)

                # Wait for the print dialog to appear
                pyautogui.sleep(2)
                # Press the "Enter" key to confirm printing
                pyautogui.press('enter')

                time.sleep(5)

                self.driver.quit()
                
                break  # exit the loop if successful
            except Exception as e:
                print(f'Error: {str(e)}')
                if i < 2:
                    print(f'Retrying in 3 seconds... (attempt {i+1}/3)')
                    time.sleep(3)
                    self.driver.quit()
                    self.driver = webdriver.Chrome(options=self.options)
                    print('Driver reinitialized.')                    
                else:
                    print('Failed after 3 attempts.')
                    self.driver.quit()
                    return False
        return True

    def print_express_with_form(self, orders):
        pass

class ExpressPrinterS(ExpressPrinter):
    def __init__(self, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path=None):
        super().__init__(username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path)
        print("ExpressPrinterS __init__")

    def print_express_with_file(self):
        for i in range(3):
            try:
                self.driver.get(self.login_url)
                logged_in_element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, self.logged_in_element_class)))
                print('Logged in already!')
            except:
                # element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//input[@type='radio' and @name='tab2']")))
                # element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.ID, 'tab02')))
                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//label[@for='tab02']")))
                element.click()

                username_field = self.driver.find_element(By.NAME, self.username_field_name)
                password_field = self.driver.find_element(By.NAME, self.password_field_name)
                username_field.send_keys(self.username)
                password_field.send_keys(self.password)
                password_field.send_keys(Keys.RETURN)
                print('Logged in successfully!')
            
            try:
                element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'svcMenuLimited-0')))
                self.driver.execute_script("window.scrollBy(0, 200)")
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().perform()
                print('click 送り状を発行する')

                # wait for the pop-up page to load
                time.sleep(8)
                # switch to the pop-up window
                popup_window_handle = self.driver.window_handles[-1]
                self.driver.switch_to.window(popup_window_handle)
                
                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='syuDTori']")))
                element.click()
                print('click 送り状データ取込')

                time.sleep(2)

                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//label[contains(@class, 'ra-radio-3')]")))
                element.click()
                print('click 独自テンプレートを使用')

                time.sleep(2)

                select_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "select-dokujiTemplSelectBox")))
                actions = ActionChains(self.driver)
                actions.move_to_element(select_element).click().perform()

                time.sleep(1)

                # 定位class包含el-select-dropdown__wrap的div元素
                element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'el-select-dropdown__wrap')]")))
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", element)

                print('scroll the el-select-dropdown__wrap div')

                time.sleep(2)

                option_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'GET')]/parent::li")))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", option_element)
                actions = ActionChains(self.driver)
                actions.move_to_element(option_element).click().perform()
                # option_element.click()
                print('select GET')

                element = self.driver.execute_script("return document.getElementsByName('files')[0];")
                self.driver.execute_script("arguments[0].style.display = 'block';", element)
                
                element.send_keys(ORDER_FOR_EXPRESS_PATH)
                print('set ファイルを選択 upload file')

                time.sleep(1)

                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '直接取込')]/parent::button")))
                element.click()
                print('click 直接取込')

                time.sleep(2)

                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '登録')]/parent::button")))
                element.click()
                print('click 登録')
                
                '''
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.F12)
                print('click F12 for 直接取込')

                time.sleep(0.5)

                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.F12)
                print('click F12 for 登録')
                '''

                time.sleep(5)

                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[@title='全て選択/取消']")))
                element.click()
                print('click 全て選択/取消')

                element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//span[(text()='印刷')]/parent::button")))
                element.click()
                print('click preview 印刷')

                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'f12')]")))
                element.click()
                print('click 印刷')

                '''
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.F12)
                print('click F12 for preview 印刷')

                time.sleep(5)

                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.F12)
                print('click F12 for 印刷')
                '''

                time.sleep(10)

                self.driver.quit()
                
                break  # exit the loop if successful
            except Exception as e:
                print(f'Error: {str(e)}')
                if i < 2:
                    print(f'Retrying in 5 seconds... (attempt {i+1}/3)')
                    time.sleep(3)
                    self.driver.quit()
                    self.driver = webdriver.Chrome(options=self.options)
                    print('Driver reinitialized.')
                else:
                    print('Failed after 3 attempts.')
                    self.driver.quit()
                    return False
        return True

    def print_express_with_form(self, orders):
        self.print_message('start printing ...')
        current_time = datetime.datetime.now()
        if not self.logged_in or (current_time - self.login_time).total_seconds() > 12 * 3600:
            self.driver.get(self.login_url)
            # try:
            #     logged_in_element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, self.logged_in_element_class)))
            #     self.print_message('Logged in already!')
            # except:
            element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//label[@for='tab02']")))
            element.click()

            username_field = self.driver.find_element(By.NAME, self.username_field_name)
            password_field = self.driver.find_element(By.NAME, self.password_field_name)
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)

            self.logged_in = True
            self.login_time = datetime.datetime.now()
            self.print_message('Logged in successfully !')
        
            # 等待页面跳转完成
            WebDriverWait(self.driver, 10).until(EC.url_changes(self.driver.current_url))

            element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='okjSksei']")))
            element.click()
            self.print_message('送り状作成')

            element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '飛脚宅配便')]/parent::button")))
            element.click()
            self.print_message('飛脚宅配便')

            WebDriverWait(self.driver, 10).until(EC.url_changes(self.driver.current_url))
        for order in orders:
            try:
                ###
                self.input_text('input-otdkSkTel', order.get("TEL", ""), '電話番号')
                self.input_text('input-otdkSkYbn', order.get("ZIP", ""), '郵便番号')
                self.input_text('input-otdkSkJsy1', order.get("Address", "")[:16], '住所１')
                self.input_text('input-otdkSkJsy2', order.get("Address", "")[16:32], '住所２')
                self.input_text('input-otdkSkJsy3', order.get("Address", "")[32:], '住所３')
                self.input_text('input-otdkSkNm1', order.get("Name", "")[:16], '名称１')
                self.input_text('input-otdkSkNm2', order.get("Name", "")[16:32], '名称２')
                self.input_text('input-kyakuKnrNo', order.get("OrNO", "")[:16], 'お客様管理番号')
                self.input_text('input-hinNm-1', order.get("Comment1", ""), '品名１')
                self.input_text('input-hinNm-2', order.get("Comment2", ""), '品名２')
                self.input_text('input-hinNm-3', order.get("Comment3", ""), '品名３')
                self.input_text('input-hinNm-4', order.get("Comment4", ""), '品名４')
                self.input_text('input-hinNm-5', order.get("Comment4", ""), '品名５')

                ###
                element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.open-control-button-to-right:not([style*="display: none"])')))
                self.driver.execute_script("arguments[0].click();", element)
                self.print_message('ご依頼主')

                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.el-select[data-vv-as="印字指定"]'))
                )
                element.click()
                self.print_message('印字指定')

                option_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '荷送人を印字する')]/parent::li")))
                option_element.click()
                self.print_message('荷送人を印字する')

                self.input_text('input-irainusiTel', order.get("ShipperTel", ""), '電話番号')
                self.input_text('input-irainusiYubin', order.get("ShipperZIP", ""), '郵便番号')
                self.input_text('input-irainusiJyusyo1', order.get("ShipperAddress", "")[0:16], '住所１')
                self.input_text('input-irainusiJyusyo2', order.get("ShipperAddress", "")[16:], '住所２')
                self.input_text('input-irainusiNm1', order.get("ShipperName", "")[:16], '名称１')
                self.input_text('input-irainusiNm2', order.get("ShipperName", "")[16:32], '名称２')                    

                ###
                d_date = order.get("D_Date", "")
                if d_date:
                    self.input_text('picker-siddHai', d_date, '指定日配達')

                d_time = self.convert_d_time(order.get("D_Time", ""))
                if d_time:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.el-select[data-vv-as="時間帯指定"]'))
                    )
                    self.driver.execute_script("arguments[0].click();", element)
                    self.print_message('時間帯指定')

                    option_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//span[(text()='{d_time}')]/parent::li")))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", option_element)
                    actions = ActionChains(self.driver)
                    actions.move_to_element(option_element).click().perform()
                    # option_element.click()
                    self.print_message(f'時間帯指定: {d_time}')

                ###
                body = self.driver.find_element(By.TAG_NAME, 'body')

                ActionChains(self.driver).move_to_element(body).send_keys(Keys.ESCAPE).perform()
                self.print_message('ESC')
                ActionChains(self.driver).move_to_element(body).send_keys(Keys.ESCAPE).perform()
                self.print_message('ESC')
                ActionChains(self.driver).move_to_element(body).send_keys(Keys.F12).perform()
                self.print_message('printing ...')

                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'f12')]")))
                element.click()
                self.print_message('downloading ...')

                time.sleep(3)
                downloaded_files = self.check_download_finish()

                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'el-message-box__headerbtn')]")))
                self.driver.execute_script("arguments[0].click();", element)
                self.print_message('close tip')

                # element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'OK')]/parent::button")))
                # element.click()
                # self.print_message('click OK')

                self.print_message(f'download finished: {order.get("OrNO", "")[:16]} {str(downloaded_files)}')
            
            except Exception as e:
                self.driver.quit()
                self.update_loading_text.emit('')
                raise(e)
        self.update_loading_text.emit('')
        return True