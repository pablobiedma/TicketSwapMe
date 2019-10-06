
from selenium import webdriver as wd
from selenium.common.exceptions import NoSuchElementException
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
        # options = Options()
        # options.add_argument('--headless')

        # self.driver = wd.Firefox(options=options)
        self.driver = wd.Firefox()

        self.login()
        self.has_tickets = False

    def login(self):
        username = 'insert facebook email here'
        password = 'insert facebook password here'

        self.driver.get(HOST)
        login_button = self.driver.find_element_by_xpath(
            "/html/body/div/div[2]/div[1]/div[1]/div/nav/ul/li[4]/button")  # make sure that class name is still the same
        login_button.click()
        time.sleep(3)
        facebook_button = self.driver.find_elements_by_xpath(
            "//*[contains(text(), 'Continue with Facebook')]"
        )[1]  # make sure that class name is still the same
        facebook_button.click()
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(4)
        user_input = self.driver.find_element_by_id('email')
        pass_input = self.driver.find_element_by_id('pass')

        user_input.send_keys(username)
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.RETURN)
        # time.sleep(3)
        self.driver.switch_to.window(self.driver.window_handles[0])
        # event_url = 'https://www.ticketswap.com/event/rodrigo-y-gabriela/85fe5b6d-f387-41d5-b324-97742f73c699'  # maybe hardcode it for more efficiency
        #
        # driver.get(event_url)


        self.cookies = self.__handle_cookies(self.driver.get_cookies())

        # driver.quit()

    def __handle_cookies(self, cookie_list):
        cookies = {}
        for cookie in cookie_list:
            cookies[cookie['name']] = cookie['value']
        return cookies

    def start(self):
        time.sleep(7)
        self.driver.get('insert url here')
        # self.driver.get('https://www.ticketswap.com/event/into-the-woods-ade/89b5d1e8-ef7f-45bc-bcbc-2a97c026802d')

        while True:
            # self.driver.get_cookies()
            time.sleep(3)

            letter=self.driver.find_element_by_css_selector('div.css-1nxi1g2:nth-child(1) > h2:nth-child(1)').text
            if(int(letter)>0):
                print(str(letter)+" are available")
                try:
                    self.driver.find_element_by_css_selector(
                    'div.css-uirvwh:nth-child(2) > ul:nth-child(1) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1)').click()
            #    self.driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/div[1]/ul/div[1]/a').click()
                #
                    time.sleep(3)
                    self.driver.find_element_by_css_selector('.css-1aros5x').click()
                except NoSuchElementException:
                    print("")
                #
                #    self.driver.find_element_by_xpath('/html/body/div/div[2]/div[1]/div/form/button').click()
                try:
                    self.driver.find_element_by_xpath('/html/body/div/div[3]/div[3]/div/a[1]/div').click()
                    time.sleep(3)
                    self.driver.find_element_by_css_selector('div.css-uirvwh:nth-child(2) > ul:nth-child(1) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1)').click()
                    #
                    time.sleep(3)
                    self.driver.find_element_by_css_selector('.css-1aros5x').click()
                except NoSuchElementException:
                    print("")

                break
            else:
                print( "No tickets are available keep trying")
            self.driver.refresh()



        # while self.has_tickets is False:
        #     print('Checking for tickets')
        #     self.get_ticket(event_url)
        #     # if data is not False:
        #     #     self.reserve_ticket(data)
        #     #     self.has_tickets = True
        #     #     webbrowser.open(HOST + '/cart', new=2)
        #     time.sleep(0.5)

    def get_ticket(self, event_url):
        """ Get Cheapest ticket """
        # Getting the cheapest ticket
        self.driver.get(event_url)

        # response = requests.get(event_url, cookies=self.cookies)
        # html = response.content.decode("utf-8")
        # parsed_html = BeautifulSoup(html, "html.parser")
        # not_exist = parsed_html.body.find('div', attrs={'class': "no-tickets"})
        # if not_exist is not None:
        #     print("no tickets")
        #     return False
        # url_object = parsed_html.body.findAll('div', attrs={'class': 'listings-item--title'})
        # if url_object is None:
        #     print("no offers")
        #     return False
        # for item in url_object:
        #     item = item.findAll('a')[0]
        #     attributes = item.attrs
        #     ticket_link = attributes['href']
        #     data = self.explode_ticket(ticket_link)
        #     if data is not False:
        #         return data
        #     print('Possible that you have the wrong event url')
        # return False

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
    t = TicketSwapMe()
    t.start()
