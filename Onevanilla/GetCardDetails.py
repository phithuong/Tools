import os
import sys
import platform
import json
import csv
import time
import requests
import argparse
import copy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


import undetected_chromedriver as uc
if (platform.system() == "Linux"):
    uc.install(executable_path='./chromedriver')
# elif (platform.system() == "Windows"):
#     uc.install(executable_path='./chromedriver.exe')

import anticaptchaofficial.recaptchav2proxyless as anticaptcha_off
import anticaptchaofficial.recaptchav2proxyon as anticaptcha_on
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

WRK_DIR = os.path.dirname(os.path.abspath(__file__))
SETTING_FILE_PATH = os.path.join(WRK_DIR, "settings.json")


class Configuration:
    @staticmethod
    def read_config(config_file_path):
        with open(config_file_path, mode='r', encoding='utf-8') as f:
            config = json.load(f)
            for key, val in config.items():
                if (key in ['api_key', 'website_url', 'website_key']) and (val == ''):
                    print('{} is not found in configuration file or the value is blank'.format(key))
                    return None
            return config


class ResolveCaptcha:
    @staticmethod
    def resolve_with_2captcha(config):
        response = {
            'error': '',
            'g_response': ''
        }
        try:
            # Create request for resolve captcha
            url = 'http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}'.format(
                config['api_key'],
                config['website_key'],
                config['website_url'])

            resp = requests.get(url)

            if resp.text[0:2] != 'OK':
                response['status'] = resp.text
                return response

            # Get response
            captcha_id = resp.text[3:]
            fetch_url = 'http://2captcha.com/res.php?key={}&action=get&id={}'.format(
                config['api_key'],
                captcha_id
            )

            for i in range(1, 10):
                time.sleep(5)  # wait 5 sec.
                resp = requests.get(fetch_url)
                if resp.text[0:2] == 'OK':
                    break

            response['g_response'] = resp.text[3:]

        except Exception as Ex:
            response['error'] = str(Ex)

        return response

    @staticmethod
    def resolve_with_anticaptcha(config):
        response = {
            'error': '',
            'g_response': ''
        }
        try:
            client = AnticaptchaClient(config['api_key'])
            task = NoCaptchaTaskProxylessTask(config['website_url'], config['website_key'], None, True)
            job = client.createTask(task)
            job.join()

            response['g_response'] = job.get_solution_response()

        except Exception as Ex:
            response['error'] = str(Ex)

        return response


class document_ready:
    def __call__(self, driver):
        document_state = driver.execute_script('return document.readyState')
        if document_state == 'complete':
            return True
        else:
            return False


class Main:
    def __init__(self, card_info_input_file_path, card_info_output_file_path, config_file_path='./setting.json',
    is_create_new_output_file=True):

        self._config = Configuration.read_config(config_file_path)
        self._card_info_input_file_path = card_info_input_file_path
        self._card_info_output_file_path = card_info_output_file_path
        self._is_create_new_output_file = is_create_new_output_file

        # Get current cards
        self._num_card = 0
        with open(card_info_input_file_path, mode='r') as cards_file:
            reader = csv.DictReader(cards_file,
                                    fieldnames=['Number', 'Month', 'Year', 'CVV'])
            headers = next(reader, None)
            for row in reader:
                self._num_card += 1

        self._card_success_list = []
        self._card_error_list = []
        if not self._is_create_new_output_file:
            with open(self._card_info_output_file_path, mode='r') as cards_details:
                reader = csv.DictReader(cards_details,
                                        fieldnames=['Number', 'Month', 'Year', 'CVV', 'Balance', 'Status', 'Transactions'])
                headers = next(reader, None)
                for row in reader:
                    if row['Balance'] != '':
                        self._card_success_list.append(row['Number'])
                    else:
                        self._card_error_list.append(row['Number'])

        self._num_card_need_get_info = self._num_card - len(self._card_success_list)

        # Proxy
        self._proxy_list = []
        self._proxy_success_list = []
        self._proxy_error_list = []


    def get_proxy(self):
        with open(self._config['proxy_list_file_path'], mode='r', encoding='utf-8') as f:
            all_lines = f.readlines()
            for line in all_lines:
                self._proxy_list.append(line.strip())

        for proxy in self._proxy_list:
            if (proxy in self._proxy_success_list) or (proxy in self._proxy_error_list):
                continue

            chrome_options = Options()
            if (platform.system() == 'Linux'):
                chrome_options.binary_location = '/usr/bin/google-chrome'
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--proxy-server={}://{}'.format(self._config['proxy_type'], proxy))
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(0)

            try:
                driver.get(self._config['website_url'])
                wait(driver, 20).until(EC.url_to_be(self._config['website_url'] + '/'))
                print('Proxy available: {}'.format(proxy))

                if proxy not in self._proxy_success_list:
                    self._proxy_success_list.append(proxy)
                    break

            except Exception as Ex:
                print('Proxy error: {}'.format(proxy))

                if proxy not in self._proxy_success_list:
                    self._proxy_error_list.append(proxy)

            finally:
                driver.quit()


    def run(self):
        self.get_proxy()

        # Main process
        cards_file = open(self._card_info_input_file_path, mode='r')
        if self._is_create_new_output_file:
            cards_details = open(self._card_info_output_file_path, 'w', newline='\n')
        else:
            cards_details = open(self._card_info_output_file_path, 'a', newline='\n')

        # Read card info
        reader = csv.DictReader(cards_file,
                                fieldnames=['Number', 'Month', 'Year', 'CVV'])
        writer = csv.DictWriter(cards_details,
                                fieldnames=['Number', 'Month', 'Year', 'CVV', 'Balance', 'Status', 'Transactions'])
        if self._is_create_new_output_file:
            writer.writeheader()

        idx = 0
        num_success = 0
        num_error = 0

        headers = next(reader, None)
        for row in reader:
            if row['Number'] in self._card_success_list:
                continue

            print('====================================================')
            print('Processing: {}'.format(row['Number']))
            print('Processed: {}/{}'.format(idx, self._num_card_need_get_info))
            print('Sucess: {}. Error: {}'.format(num_success, num_error))
            print('====================================================')

            # Create webdriver & go to target website
            if (len(self._proxy_success_list) > 0):
                proxy = self._proxy_success_list[-1]
                print('Using proxy: {}'.format(proxy))
            else:
                print("Have't valid proxy.")

            chrome_options = Options()
            if (platform.system() == 'Linux'):
                chrome_options.binary_location = '/usr/bin/google-chrome'
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--proxy-server={}://{}'.format(self._config['proxy_type'], proxy))

            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(0)
            # driver = webdriver.Chrome(ChromeDriverManager().install(), options=self._chrome_options)
            driver.set_window_size(1024, 800)
            driver.get(self._config['website_url'])
            time.sleep(20)

            try:
                idx += 1

                # Input value to fields by selenium driver
                cardnumber = driver.find_element_by_id('cardnumber')
                cardnumber.send_keys(row['Number'])

                expMonth = driver.find_element_by_id('expMonth')
                expMonth.send_keys(row['Month'])

                expirationYear = driver.find_element_by_id('expirationYear')
                expirationYear.send_keys(row['Year'])

                cvv = driver.find_element_by_id('cvv')
                cvv.send_keys(row['CVV'])

                driver.execute_script('document.getElementById("g-recaptcha-response").style.display = "block";')
                recaptcha_callback = driver.execute_script(
'''return (function () {
    if (typeof (___grecaptcha_cfg) !== 'undefined') {
        let cs = [];
        for (let id in ___grecaptcha_cfg.clients) {
            cs.push(id);
        }
        let res = cs.map(cid => {
            for (let p in ___grecaptcha_cfg.clients[cid]) {
                let c = {};
                cid >= 10000 ? c.version = 'V3' : c.version = 'V2';
                let path = "___grecaptcha_cfg.clients[" + cid + "]." + p;
                let pp = eval(path);
                if (typeof pp === 'object') {
                    for (let s in pp) {
                        let subpath = "___grecaptcha_cfg.clients[" + cid + "]." + p + "." + s;
                        let sp = eval(subpath);
                        if (sp && typeof sp === 'object' && sp.hasOwnProperty('sitekey') && sp.hasOwnProperty('size')) {
                            c.sitekey = eval(subpath + '.sitekey');
                            let cb = eval(subpath + '.callback');
                            if (cb == null) {
                                c.callback = null;
                                c.function = null;
                            }
                            else {
                                c.callback = subpath + '.callback';
                                cb != c.callback ? c.function = cb : c.function = null;
                            }
                        }
                    }
                }
                return c;
            }
        });
        return (res);
    } else {
        return (null);
    }
})()
''')

                # Resolve captcha
                type_captcha_idx = self._config['type_resolve_captcha_idx']
                if self._config['types_resolve_captcha'][type_captcha_idx] == '2captcha':
                    response = ResolveCaptcha.resolve_with_2captcha(self._config)
                elif self._config['types_resolve_captcha'][type_captcha_idx] == 'anticaptcha':
                    response = ResolveCaptcha.resolve_with_anticaptcha((self._config))

                # Callback to get card info
                driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML="{}";'.format(response['g_response']))
                driver.execute_script('{}("{}")'.format(recaptcha_callback[0]['callback'], response['g_response']))

                button = driver.find_element_by_id('brandLoginForm_button')
                button.click()

                # Wait until redirect to manageCard page, then get card info
                wait(driver, 20).until(EC.url_to_be('https://onevanilla.com/manageCard'))

                time.sleep(10)
                avlBalanceElement = wait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='Avlbal']/div"))
                )
                balance = avlBalanceElement.text

                statusElement = wait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='brandCardInfo']/div[3]/ul/li[3]/span"))
                )
                status = statusElement.text

                wait(driver, 5).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'app-balance-transactions > div > div > div:nth-child(2) > div:nth-child(2)')))

                transactionEls = driver.find_elements_by_css_selector(
                    'app-balance-transactions > div > div > div:nth-child(2) > div')
                transactions = []
                for transactionEl in transactionEls:
                    try:
                        transactions.append(transactionEl.text)
                    except:
                        pass

                transactionsText = (''.join(transactions)).replace('\n', ' | ')

                # Write result
                print(balance)
                print(status)
                print(transactionsText)

                if (balance is not None) and (str(balance) != ''):
                    writer.writerow({
                        'Number': str(row['Number']),
                        'Month': row['Month'],
                        'Year': row['Year'],
                        'CVV': row['CVV'],
                        'Balance': str(balance),
                        'Status': str(status),
                        'Transactions': str(transactionsText),
                    })
                    cards_details.flush()

                    num_success += 1
                    self._card_success_list.append(row['Number'])

            except Exception as Ex:
                print('{}: {}'.format(type(Ex), Ex))
                num_error += 1

                self.get_proxy()

            finally:
                driver.quit()

        print('====================================================')
        print('Processed: {}/{}'.format(self._num_card_need_get_info, self._num_card_need_get_info))
        print('Sucess: {}. Error: {}'.format(num_success, num_error))
        print('====================================================')


def main():
    parser = argparse.ArgumentParser(description='This is arguments of get card information program')
    parser.add_argument('-c', '--config_file', default='./settings.json')
    parser.add_argument('-in', '--input_file', default='./cards.csv')
    parser.add_argument('-out', '--output_file', default='./cards_details.csv')

    is_create_new_output_file = False
    is_continue = True
    while is_continue:
        x = input('You want to create new output file (Y/N): ')
        if x.strip().lower() in ['y', 'yes']:
            is_create_new_output_file = True
            print('created new output file.')
            break
        elif x.strip().lower() in ['n', 'no']:
            is_create_new_output_file = False
            print('write to previous output file.')
            break
        else:
            print('You should input [y, n, yes, no]')

    args = parser.parse_args()
    print('====================================================')
    print('Running with flowing arguments:')
    print('Config file path: {}'.format(args.config_file))
    print('Input file path: {}'.format(args.input_file))
    print('Output file path: {}'.format(args.output_file))
    print('Create new output file: {}'.format(is_create_new_output_file))
    print('====================================================')

    program = Main(args.input_file,
                    args.output_file,
                    config_file_path=args.config_file,
                    is_create_new_output_file=is_create_new_output_file)

    program.run()


if __name__=='__main__':
    main()
