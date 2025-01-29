from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import keyboard
import os

class CookieClickerBot:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.chrome_options = self._set_options()
        self.service = Service(executable_path='./chromedriver.exe')
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.url = "https://cookieclicker.ee/"

    def _set_options(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.current_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--start-maximized")
        return chrome_options       


    def _click_cookie(self):
        self.cookie.click()

    def save_game(self):
        # Open options menu
        try:
            self.driver.find_element(By.ID, "prefsButton").click()
            print("Options menu opened!")

            # Close achievements if they are open
            try:
                achievements = self.driver.find_element(By.CSS_SELECTOR, ".framed.close.sidenote")
                print("Found achievements", achievements)
                achievements.click()
            except:
                pass

            # Click save button
            print("Searching for save button...")
            save_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Save to file')]")
            print("Clicking save button...", save_button)
            save_button.click()

            # If successful, remove old save file
            print("Removing old save file...")
            if self.save_file:
                os.remove(os.path.join(self.current_dir, self.save_file))

            time.sleep(3)

        except Exception as e:
            print("Error saving game!", e)

    
    def load_save(self):
        # Load save if it exists
        # Look for txt file in current directory
        files = os.listdir(self.current_dir)
        self.save_file = None
        for file in files:
            if file.endswith(".txt"):
                self.save_file = file
                break
        try:
            with open(self.save_file, "r", encoding="utf-8-sig") as f:
                save = f.read().strip()
                print(save)
                # Paste save
                # Shortcut: Ctrl + O
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + 'o')
                time.sleep(1)

                # Close popup if open
                try:
                    achievements = self.driver.find_element(By.CSS_SELECTOR, ".close")
                    achievements.click()
                except:
                    pass

                # Paste save
                text_box = self.driver.find_element(By.ID, "textareaPrompt")
                text_box.clear()
                text_box.send_keys(save)

                # Press Enter
                text_box.send_keys(Keys.ENTER)

                time.sleep(5)

        except:
            print("No save found!")

    def _buy_products(self, n_cookies):
        # Find products
        try:
            products = self.driver.find_elements(By.CSS_SELECTOR, ".product.unlocked.enabled")
            for product in products[::-1]:
                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView();", product)

                # Find product price
                print("Obtaining product price...")
                product_price = product.find_element(By.CSS_SELECTOR, ".price").text
                try:
                    # Obtain product price
                    product_price = int(product_price.replace(",", ""))

                    # Purchase product as many times as possible
                    while n_cookies >= product_price:
                        print("Product price: ", product_price)
                        print("Cookies: ", n_cookies)
                        # Purchase product
                        product.click()
                        n_cookies -= product_price
                        product_price = product.find_element(By.CSS_SELECTOR, ".price").text
                        product_price = int(product_price.replace(",", ""))
                except:
                    continue

        except:
            pass

    def _buy_crates(self):
        try:
            # Find crates
            crates = self.driver.find_elements(By.CSS_SELECTOR, ".crate.upgrade.enabled")
            for crate in crates[::-1]:
                print("Buying crate...")
                crate.click()
        except:
            pass

    def _handle_language(self):
        # Handle language selection if it appears
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'English')]"))
            )
            language = self.driver.find_element(By.XPATH, "//*[contains(text(), 'English')]")
            language.click()
        except:
            pass

    def play_game(self):
        self.driver.get(self.url)
        # Handle language selection if it appears
        self._handle_language()
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "bigCookie"))
        )

        self.cookie = self.driver.find_element(By.ID, "bigCookie")
        self.cookies_id = "cookies"
        self.load_save()

        # Click cookies 
        n = 5
        playing = True
        while playing:  

            # Click cookie for n serconds
            start_time = time.time()
            while time.time() - start_time < n:
                if keyboard.is_pressed('q'):
                    playing = False
                    self.save_game()
                    break
                self._click_cookie()

            if not playing:
                break

            n_cookies = self.driver.find_element(By.ID, self.cookies_id).text
            n_cookies = int(n_cookies.replace(",", "").split(' ')[0])

            # Buy products
            self._buy_products(n_cookies)
            # Buy crates
            self._buy_crates()

        self.driver.quit()

        
if __name__ == "__main__":

    bot = CookieClickerBot()
    bot.play_game()