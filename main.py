from selenium import webdriver as wd
from selenium.webdriver.common.keys import Keys
import json
import time
import requests
import getpass
import webbrowser

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

HOST = "https://www.ticketswap.nl"

class TicketSwapMe:
    def __index__(self):
        self.login()
        self.has_tickets = False

    def login(self):
        username = input("Facebook username:  ")
        password = getpass.getpass("Facebook password:  ")
        driver = wd.Firefox()
        driver.get(HOST)
        login_button = driver.find_element_by_class_name("css-1ia6hlk e1oaf4hi6")  #make sure that class name is still the same
        login_button.click()
        time.sleep(3)
        facebook_button = driver.find_element_by_class_name("css-xl214v e1suhhn80") #make sure that class name is still the same
        facebook_button.click()
        time.sleep(1)

        driver.switch_to_window(driver.window_handles[1])
        user_input = driver.find_element_by_id('email')
        pass_input = driver.find_element_by_id('pass')

        user_input.send_keys(username)
        pass_input.send_keys(password)
