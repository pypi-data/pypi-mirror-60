import traceback
import os
import platform
from re import sub
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from pytz import timezone

__all__ = ['BaseDriver']


def simple_traceback(limit=7) -> str:
    stack_trace = traceback.extract_stack(limit=limit)[:-2]
    return "\n".join(":".join((os.path.basename(filename),
                               function_name,
                               str(line_number),))
                     for filename, line_number, function_name, text
                     in stack_trace)


def wait_enabled(element: WebElement):
    while not element.is_enabled():
        sleep(1)


def wait_displayed(element: WebElement):
    while not element.is_displayed():
        sleep(1)


def get_money_from_text(text) -> int:
    t = sub(r'[^\d.]', '', text)
    return int(t) if t else 0


def esc_xpath(s) -> str:
    if "'" not in s:
        return "'%s'" % s
    if '"' not in s:
        return '"%s"' % s
    return "concat('%s')" % s.replace("'", "',\"'\",'")


def get_chrome(is_headless=False, disable_images=False) -> webdriver.Chrome:
    options = Options()
    if is_headless:
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)


class BaseDriver:
    timeout = 10
    
    def __init__(self, debug_path='/tmp/webdriver/debug', **kwargs):
        self.browser = get_chrome(**kwargs)
        self.browser.set_page_load_timeout(30)
        self.browser.set_script_timeout(10)
        self.wait = ui.WebDriverWait(self.browser, self.timeout)
        self.debug_path = debug_path

        if not os.path.isdir(self.debug_path):
            os.makedirs(self.debug_path)

    def debug(self, e=None):
        print(f"********\n"
              f"URL: {self.browser.current_url}\n"
              f"{e}\n"
              f"{simple_traceback()}\n")
        timestamp = datetime.now(timezone('Asia/Tokyo')).replace(tzinfo=None).strftime("%Y%m%d_%H%M")
        filename = f'{self.debug_path}/{self.__class__.__name__}_{timestamp}'
        snapfile = filename + '.png'
        self.browser.save_screenshot(snapfile)
        print("\nScreenshot saved as ", snapfile)

        htmlfile = filename + '.html'
        with open(htmlfile, 'w') as f:
            f.write(self.browser.page_source)

    def new_window(self) -> bool:
        body = self.wait.until(lambda b: b.find_element_by_css_selector("body"))
        body.send_keys(Keys.CONTROL + "t")
        return True
        
    def close_window(self) -> bool:
        body = self.wait.until(lambda b: b.find_element_by_css_selector("body"))
        body.send_keys(Keys.CONTROL + "w")
        return True

    def close(self):
        for window in self.browser.window_handles:
            self.browser.switch_to.window(window)
            self.browser.close()
        self.browser.quit()
