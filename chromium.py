import json
import platform
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

class chromium():
    def __init__(self):
        # Set up Chrome options to connect to the already running browser
        options = Options()

        if platform.system() == "Windows":
            options.debugger_address = "127.0.0.1:9222"
        elif platform.system() == "Linux":
            options.add_argument("--remote-debugging-port=9222") 

        # Set up the driver to connect to the open browser
        driver = webdriver.Chrome(options=options)
        self.driver = driver
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

    def add_new_item(self, parent) -> str:
        '''Adds a new element to "repeating_moves" or "repeating_abilities" and returns str id of new element.'''
        # Find the repcontainer that contains all moves
        css_selector = f"div[data-groupname='{parent}']"
        repcontainer = self.driver.find_element(By.CSS_SELECTOR, f"{css_selector}.repcontainer")
        # Get the elements inside of the repcontainer.
        original_elements = repcontainer.find_elements(By.XPATH, "./*")
        original_count = len(original_elements)
        # Get the IDs of the elements in the container
        rep_ids = [element.get_attribute("data-reprowid") for element in original_elements]
        if len(rep_ids) == 0: rep_ids = ["1"]
        # Loop until a new element is successfully added
        while True:
            self.driver.execute_script(f"""
                let element = document.querySelector("{css_selector} .btn.repcontrol_add");
                element.click();
                element.dispatchEvent(new Event('change')); 
                element.dispatchEvent(new Event('blur')); 
                element.dispatchEvent(new Event('input'));
            """)

            # Wait 100ms for roll20 to respond to click
            time.sleep(0.1)

            # Wait 1 seconds for the new element to appear.
            try:
                WebDriverWait(self.driver, 1).until(
                    lambda _: len(self.driver.find_element(By.CSS_SELECTOR, f"{css_selector}.repcontainer").find_elements(By.XPATH, "./*")) > original_count
                )
            except:
                continue

            # Sometimes roll20 just deletes the element for no reason
            try:
                # Find the repcontainer that contains all moves
                repcontainer = self.driver.find_element(By.CSS_SELECTOR,  f"{css_selector}.repcontainer")

                # Get all elements again.
                new_elements = repcontainer.find_elements(By.XPATH, "./*")

                # Get the newest element.
                new_element = new_elements[-1]

                # Extract the ID
                new_element_id = new_element.get_attribute("data-reprowid")
            except:
                continue

            # Check if ID is actually new
            if new_element_id != rep_ids[-1]:
                break
        return new_element_id
    
    def submit_fields(self, css_selector, input):
        '''Updates an <element> with a new value and sends signal.'''
        self.driver.execute_script(f"""
            let element = document.querySelector('{css_selector}');
            element.value = '{input}';
            element.dispatchEvent(new Event('change')); 
            element.dispatchEvent(new Event('blur')); 
            element.dispatchEvent(new Event('input'));
        """)

    def submit_selection(self, css_selector, option_text):
        """Selects an option within a <select> element by its text content."""
        input_field = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        for field in input_field:
            if not field.is_displayed(): continue
            ActionChains(self.driver).move_to_element(field).perform()
            time.sleep(0.01)
            field.send_keys(option_text)
            field.send_keys(Keys.RETURN)
            field.send_keys(Keys.RETURN)

    def submit_checkbox(self, css_selector):
        css_selector = css_selector.replace("checkbox","input")
        self.driver.execute_script(f"""
            let element = document.querySelector('{css_selector}');
            element.click();
            element.dispatchEvent(new Event('change')); 
            element.dispatchEvent(new Event('blur')); 
            element.dispatchEvent(new Event('input'));
        """)
    
    def edit_item_element(self, parent, datatype, dataset, input) -> None:
        '''Edit a move or ability sub-element'''
        parent_id = json.dumps(parent)
        css_selector = f"div[data-reprowid={parent_id}] {datatype}[name=\"{dataset}\"]"
        if datatype != "select" and datatype != "checkbox":
            self.submit_fields(css_selector, input)
        elif datatype != "select" and datatype == "checkbox":
            self.submit_checkbox(css_selector)
        else:
            self.submit_selection(css_selector, input)

    def find_input(self, dataset, input):
        '''Find an element and update its field'''
        css_selector = f"input[name=\"{dataset}\"]"
        self.submit_fields(css_selector, input)

    def find_textarea(self,dataset,input):
        '''Search for an input field and edit it'''
        css_selector = f"textarea[name=\"{dataset}\"]"
        self.submit_fields(css_selector, input)

if __name__ == "__main__":
    chrome = chromium()
    chrome.find_roll20()
    chrome.close()