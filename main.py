from selenium import webdriver as wd
from selenium.webdriver.common.keys import Keys
import json
import time
import requests
import getpass
import tkinter as tk
from tkinter import simpledialog
import webbrowser

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

HOST = "https://www.ticketswap.com"


class TicketSwapMe:
    def __init__(self, username, password):
        self.login()
        self.username = username
        self.password = password
        self.driver = wd.Firefox()
        self.has_tickets = False

    def login(self):

        driver = self.driver
        driver.get("https://www.ticketswap.com")
        login_button = driver.find_element_by_class_name(
            "css-1ia6hlk e1oaf4hi6")  # make sure that class name is still the same
        login_button.click()
        time.sleep(3)
        facebook_button = driver.find_element_by_class_name(
            "css-xl214v e1suhhn80")  # make sure that class name is still the same
        facebook_button.click()
        time.sleep(1)

        driver.switch_to_window(driver.window_handles[1])
        user_input = driver.find_element_by_id('email')
        pass_input = driver.find_element_by_id('pass')

        user_input.send_keys(self.username)
        pass_input.send_keys(self.password)
        if driver.find_element_by_id('loginbutton'):
            send_login = driver.find_element_by_id('loginbutton')

        elif driver.find_element_by_id('u_0_0'):
            send_login = driver.find_element_by_id('u_0_0')

            send_login.click()
            time.sleep(1)

        try:
            confirm = driver.find_element_by_name('__CONFIRM__')

            confirm.click()

            time.sleep(1)
        except Exception:
            pass

        driver.switch_to_window(driver.window_handles[0])

        time.sleep(3)

        self.cookies = self.__handle_cookies(driver.get_cookies())

        driver.quit()

        if 'token' not in self.cookies:
            print('username or password is invalid!')
            self.login()

    def __handle_cookies(self, cookieList):
        cookies = {}
        for cookie in cookieList:
            cookies[cookie['name']] = cookie['value']
        return cookies

    def start(self):
        event_url = simpledialog.askstring(title="Event URL",
                                           prompt="Please enter the event URL: ")  # maybe hardcode it for more efficiency
        while self.has_tickets is False:
            print('Checking for tickets')
            data = self.get_ticket(event_url)
            if data is not False:
                self.reserve_ticket(data)
                self.has_tickets = True
                wd.open(HOST + '/cart', new=2)
            time.sleep(0.5)

    def get_ticket(self, event_url):
        """ Get Cheapest ticket """
        # Getting the cheapest ticket
        response = requests.get(event_url, cookies=self.cookies)
        html = response.content.decode("utf-8")
        parsed_html = BeautifulSoup(html, "html.parser")
        not_exist = parsed_html.body.find('div', attrs={'class': "no-tickets"})
        if not_exist is not None:
            print("no tickets")
            return False
        url_object = parsed_html.body.findAll('div', attrs={'class': 'listings-item--title'})
        if url_object is None:
            print("no offers")
            return False
        for item in url_object:
            item = item.findAll('a')[0]
            attributes = item.attrs
            ticket_link = attributes['href']
            data = self.explode_ticket(ticket_link)
            if data is not False:
                return data
        print('Possible that you have the wrong event url')
        return False

    def explode_ticket(self, ticket_link):
        """ Gets tokens from ticket page """
        # Get tokens that you need to have to reserve the ticket and getting the get in cart link
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
        # check type of ticket
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
        # add ticket in cart
        ticket = requests.post(HOST + content['ticket_link'], data=form_data, cookies=self.cookies)
        content = json.loads(ticket.content.decode("utf-8"))
        print('Successfully added ticket to your account')
        return bool(content['success'])


if __name__ == "__main__":
    ROOT = tk.Tk()
    ROOT.withdraw()
    username = simpledialog.askstring(title="Username",
                                      prompt="Please enter your instagram username: ")
    password = simpledialog.askstring(title="Password",
                                      prompt="Please enter your password: ",
                                      show="*")
    t = TicketSwapMe()
    t.login()
    t.start()
