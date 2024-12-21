from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
# chromium --remote-debugging-port=9222 --user-data-dir=/home/josh/.config/chromium

class chromium():
    def __init__(self):
        # Set up Chrome options to connect to the already running browser
        options = Options()
        options.add_argument("--remote-debugging-port=9222")  # Match the port from the previous command

        # Set up the driver to connect to the open browser
        driver = webdriver.Chrome(options=options)
        self.driver = driver
        self.name = 'None'
        self.found = False

    def close(self):
        self.driver.quit()

    def find_roll20(self):
        # Get all window handles
        windows = self.driver.window_handles
        for window in windows:
            self.driver.switch_to.window(window)
            element = self.driver.find_elements(By.XPATH, '//iframe[contains(@title, "Character sheet for")]')
            if element:
                self.driver.switch_to.frame(element[0])
                self.found = True
                break
        if not self.found:
            print('Could not locate roll20 character sheet, is one open?')
            exit()

    def find_button(self,dataset):
        '''Search for a button and click it'''
        buttons = self.driver.find_elements(By.XPATH, "//button[text()='+Add']")

        for button in buttons:
            parent = button.find_element(By.XPATH, "./..")  # Select the direct parent node
            if not button.is_displayed(): continue
            if dataset not in parent.get_attribute('outerHTML'): continue
            ActionChains(self.driver).move_to_element(button).perform()
            time.sleep(0.1)
            button.click()
            break

    def find_input(self,dataset,input):
        '''Search for an input field and edit it'''
        input_field = self.driver.find_elements(By.CSS_SELECTOR, f'input[name="{dataset}"]')
        if not input_field: return
        for field in input_field:
            if not field.is_displayed(): continue
            if 'Ability' in dataset:
                if field.get_attribute("value"): continue
            ActionChains(self.driver).move_to_element(field).perform()
            time.sleep(0.01)
            field.clear()
            field.send_keys(input)
            field.send_keys(Keys.RETURN)
            time.sleep(0.01)

    def find_textarea(self,dataset,input):
        '''Search for an input field and edit it'''
        input_field = self.driver.find_elements(By.CSS_SELECTOR, f'textarea[name="{dataset}"]')
        if not input_field: return
        for field in input_field:
            if not field.is_displayed(): continue
            ActionChains(self.driver).move_to_element(field).perform()
            time.sleep(0.1)
            field.clear()
            field.send_keys(input)
            time.sleep(0.1)

    def find_move_parent(self):
        '''Find the new move container'''
        parent_element = self.driver.find_elements(By.XPATH, "//input[@name='attr_mlName']/../../..")
        for parent in parent_element:
            child = parent.find_element(By.NAME, "attr_mlName")
            # There are invisible template forms that we cant write to
            if not child.is_displayed(): continue
            # If there is something in the field dont write in it
            if child.get_attribute('value'): continue
            # If we reach this point we know this is the new empty move
            break
        return parent
    
    def find_ability_parent(self):
        '''Find the new move container'''
        parent_element = self.driver.find_elements(By.XPATH, "//input[@name='attr_Ability_Name']/../..")
        for parent in parent_element:
            child = parent.find_element(By.NAME, "attr_Ability_Name")
            # There are invisible template forms that we cant write to
            if not child.is_displayed(): continue
            # If there is something in the field dont write in it
            if child.get_attribute('value'): continue
            # If we reach this point we know this is the new empty ability
            break
        return parent    

    def search_parent(self, parent, attr, input):
        children = parent.find_elements(By.NAME, attr)
        for child in children:
            if not child.is_displayed(): continue
            if child.tag_name in ['input']:
                child.clear()
            child.send_keys(input)
            child.send_keys(Keys.RETURN)
            child.send_keys(Keys.RETURN)
            time.sleep(0.2)
    