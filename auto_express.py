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

class Express(Enum):
    KURONEKOYAMATO = "kuronekoyamato"
    SAGAWAEXP = "sagawaexp"

def create_express_printer(name):
    config = database.get_express_config(name)
    if not config:
        raise ValueError("no express config for name: ", name)
    username = config['username']
    password = config['password']
    username_field_name = config['username_field_name']
    password_field_name = config['password_field_name']
    login_url = config['login_url']
    logged_in_element_class = config['logged_in_element_class']
    home_url = config['home_url']
    if name == Express.KURONEKOYAMATO.value:
        return ExpressPrinterK(username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url)
    elif name == Express.SAGAWAEXP.value:
        return ExpressPrinterS(username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url)
    else:
        raise ValueError("no express printer for name: ", name)

class ExpressPrinter(abc.ABC):
    def __init__(self, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url):
        self.options = webdriver.ChromeOptions()
        # set headless mode
        # self.options.add_argument("--headless")

        # prevent the driver from automatically closing the browser for debugging
        # self.options.add_experimental_option("detach", True)

        self.options.add_experimental_option('prefs', {'download.default_directory': 'D:\\'})
        self.options.add_argument('--enable-print-browser')
        '''
        The --kiosk-printing option is used in the provided code to enable printing in kiosk mode. 
        Kiosk mode is a full-screen mode that is commonly used in public places such as airports, museums, and libraries to provide access to information or services. 
        In kiosk mode, the browser is locked down and only allows access to a specific website or application.
        '''
        # self.options.add_argument("--kiosk-printing")
        # options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=self.options)        
        self.username = username
        self.password = password
        self.username_field_name = username_field_name
        self.password_field_name = password_field_name
        self.login_url = login_url
        self.logged_in_element_class = logged_in_element_class
        self.home_url = home_url

    @abc.abstractmethod
    def print_express(self):
        pass

class ExpressPrinterK(ExpressPrinter):
    def print_express(self):
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
                option_element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//option[text()='G09-1']")))
                option_element.click()
                print('select 取込みパターン: G09-1')
                
                element = self.driver.execute_script("return document.getElementById('filename');")
                self.driver.execute_script("arguments[0].style.display = 'block';", element)
                element.send_keys(r"E:\Wangyn\个人\Jan\RFID\K0.xlsx")    
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

                time.sleep(10)

                # Switch to the iframe that contains the PDF
                iframe = self.driver.find_element(By.XPATH, "//iframe[@class='fancybox-iframe']")
                self.driver.switch_to.frame(iframe)

                # self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'p')

                self.driver.execute_script("window.print();")

                # Wait for the print dialog to appear
                pyautogui.sleep(1)
                # Press the "Enter" key to confirm printing
                pyautogui.press('enter')

                time.sleep(5)

                self.driver.quit()
                
                break  # exit the loop if successful
            except Exception as e:
                print(f'Error: {e}')
                if i < 2:
                    print(f'Retrying in 3 seconds... (attempt {i+1}/3)')
                    time.sleep(3)
                    self.driver.close()
                    self.driver = webdriver.Chrome(options=self.options)
                    print('Driver reinitialized.')                    
                else:
                    print('Failed after 3 attempts.')
                    return False
        return True

class ExpressPrinterS(ExpressPrinter):
    def print_express(self):
        
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

                select_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "select-dokujiTemplSelectBox")))
                actions = ActionChains(self.driver)
                actions.move_to_element(select_element).click().perform()

                option_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'GEE')]/parent::li")))
                option_element.click()
                print('select GEE')

                element = self.driver.execute_script("return document.getElementsByName('files')[0];")
                self.driver.execute_script("arguments[0].style.display = 'block';", element)
                element.send_keys(r"E:\Wangyn\个人\Jan\RFID\K0.xlsx")
                print('set ファイルを選択 upload file')

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

                time.sleep(3)

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

                time.sleep(5)

                self.driver.quit()
                
                break  # exit the loop if successful
            except Exception as e:
                print(f'Error: {e}')
                if i < 2:
                    print(f'Retrying in 5 seconds... (attempt {i+1}/3)')
                    time.sleep(3)
                    self.driver.close()
                    self.driver = webdriver.Chrome(options=self.options)
                    print('Driver reinitialized.')                    
                else:
                    print('Failed after 3 attempts.')
                    return False
        return True