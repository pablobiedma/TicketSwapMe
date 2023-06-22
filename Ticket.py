from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
import time
import requests
import tkinter as tk
from tkinter import simpledialog
import webbrowser

from selenium.webdriver.firefox.options import Options

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

HOST = "https://www.ticketswap.com"

class TicketSwapMe:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.login()
        self.has_tickets = False

    def login(self):
        username = 'insert facebook email here'
        password = 'insert facebook password here'

        self.driver.get(HOST)
        login_button = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/nav/div[1]/ul/li[3]/button")
        login_button.click()
        time.sleep(3)
        facebook_button = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue with Facebook')]")[1]
        facebook_button.click()
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(4)
        user_input = self.driver.find_element(By.ID, 'email')
        pass_input = self.driver.find_element(By.ID, 'pass')

        user_input.send_keys(username)
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.RETURN)
        self.driver.switch_to.window(self.driver.window_handles[0])

        self.cookies = self.__handle_cookies(self.driver.get_cookies())

    def __handle_cookies(self, cookie_list):
        cookies = {}
        for cookie in cookie_list:
            cookies[cookie['name']] = cookie['value']
        return cookies

    def start(self):
        time.sleep(7)
        self.driver.get('insert url here')

        while True:
            time.sleep(3)

            letter = self.driver.find_element(By.CSS_SELECTOR, 'div.css-1nxi1g2:nth-child(1) > h2:nth-child(1)').text
            if int(letter) > 0:
                print(str(letter) + " are available")
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'div.css-uirvwh:nth-child(2) > ul:nth-child(1) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1)').click()
                    time.sleep(3)
                    self.driver.find_element(By.CSS_SELECTOR, '.css-1aros5x').click()
                except NoSuchElementException:
                    print("")
                try:
                    self.driver.find_element(By.XPATH, '/html/body/div/div[3]/div[3]/div/a[1]/div').click()
                    time.sleep(3)
                    self.driver.find_element(By.CSS_SELECTOR, 'div.css-uirvwh:nth-child(2) > ul:nth-child(1) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1)').click()
                    time.sleep(3)
                    self.driver.find_element(By.CSS_SELECTOR, '.css-1aros5x').click()
                except NoSuchElementException:
                    print("")

                break
            else:
                print("No tickets are available. Keep trying")
            self.driver.refresh()

    def get_ticket(self, event_url):
        """ Get Cheapest ticket """
        self.driver.get(event_url)

    def explode_ticket(self, ticket_link):
        """ Gets tokens from ticket page """
        response = requests.get(HOST + ticket_link, cookies=self.cookies)
        parsed_html = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        token_object = parsed_html.body.find('input', attrs={"name": "reserve[_token]"})
        if token_object is None:
            print("Failed to get token")
            return False
        token_attrs = token_object.attrs
        reserve_token_object = parsed_html.body.find('input', attrs={"name": "reserve[_token]"})

        if reserve_token_object is None:
            return False
        reserve_token_attrs = reserve_token_object.attrs
        add_data = {}
        seats = parsed_html.body.find('input', attrs={'name': 'tickets[]'})
        if seats is not None:
            add_data['tickets[]'] = seats.attrs['value']
        else:
            items = parsed_html.body.find('select', attrs={'name': 'amount'})
            count = len(items.findChildren())
            add_data['amount'] = count
        token = token_attrs['value']
        reserve_token = reserve_token_attrs['value']
        ticket_link_reserve = parsed_html.body.find('form', attrs={"id": "listing-reserve-form"}).attrs
        ticket_reserve_link = ticket_link_reserve['data-endpoint']
        return {"token": token,
                "reserve_token": reserve_token,
                "ticket_link": ticket_reserve_link,
                "more_data": add_data}

    def reserve_ticket(self, content):
        """ Reserve ticket """
        token = content['token']
        reserve_token = content['reserve_token']
        form_data = {"token": token, "reserve[_token]": reserve_token, **content['more_data']}
        ticket = requests.post(HOST + content['ticket_link'], data=form_data, cookies=self.cookies)
        content = json.loads(ticket.content.decode("utf-8"))
        print('Successfully added ticket to your account')
        return bool(content['success'])

if __name__ == "__main__":
    ROOT = tk.Tk()
    ROOT.withdraw()
    t = TicketSwapMe()
    t.start()
