import os
import json
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import anticaptchaofficial.recaptchav2proxyless as anticaptcha_off
import anticaptchaofficial.recaptchav2proxyon as anticaptcha_on
from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)


WRK_DIR = os.path.dirname(os.path.abspath(__file__))
SETTING_FILE_PATH = os.path.join(WRK_DIR, "settings.json")


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/getCardInfo', methods=['POST'])
def get_card_info():
    data = request.json
    print(data)

    result = selenium_run(data)

    card_info = {
        "balance": result["balance"],
        "status": result["status"],
        "checkresult": result["checkresult"],
        "note": ""
    }
    return jsonify(card_info)


def get_g_response():
    response = {
        "status": None,
        "error": None,
        "g_response": None
    }
    try:
        setting_params = _get_setting()
        if setting_params is None:
            return

        url = "http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(
            setting_params["api_key"],
            setting_params["website_key"],
            setting_params["website_url"])

        resp = requests.get(url)

        if resp.text[0:2] != 'OK':
            response["status"] = resp.text
            return response

        captcha_id = resp.text[3:]
        fetch_url = "http://2captcha.com/res.php?key={}&action=get&id={}".format(
            setting_params["api_key"],
            captcha_id
        )

        for i in range(1, 10):
            time.sleep(5)  # wait 5 sec.
            resp = requests.get(fetch_url)
            if resp.text[0:2] == 'OK':
                break

        response["status"] = 200
        response["error"] = ""
        response["g_response"] = resp.text[3:]

    except Exception as Ex:
        print(Ex)
        response["status"] = 500
        response["error"] = Ex.message

    return response


@app.route('/save_config', methods=['POST'])
def save_config():
    response = {
        "status": None,
        "error": None
    }
    try:
        new_config = request.data.decode('utf8').replace("'", '"')
        new_config = json.loads(new_config)

        before_config = _get_setting()

        for key, value in new_config.items():
            before_config[key] = value
        before_config["proxy_off"] = False

        with open(SETTING_FILE_PATH, "w") as f:
            json.dump(before_config, f, indent=4)

        response["status"] = 200

    except Exception as Ex:
        print(Ex)
        response["status"] = 500

    return response


def _get_setting():
    with open(SETTING_FILE_PATH, "r") as f:
        j = json.load(f)
        for key, val in j.items():
            if (key in ["api_key", "website_url", "website_key"]) and (val == ""):
                return None
        return j


def selenium_run(data):
    settings = _get_setting()

    try:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        if not settings["proxy_off"]:
            options.add_argument(
                '--proxy-server=socks5://{}'.format(settings["proxy"]))

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(settings["website_url"])

        time.sleep(20)
        gRecaptchaElement = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "g-recaptcha-response"))
        )

        # Get DOM of elements (form submit)
        cardNumberElement = driver.find_element_by_xpath("//input[@id='cardnumber']")
        mmElement = driver.find_element_by_xpath("//input[@id='expMonth']")
        yyElement = driver.find_element_by_xpath("//input[@id='expirationYear']")
        cvvElement = driver.find_element_by_xpath("//input[@id='cvv']")
        signInElement = driver.find_element_by_xpath("//button[@id='brandLoginForm_button']")

        cardNumberElement.send_keys(data["cardnumber"])
        mmElement.send_keys(data["mm"])
        yyElement.send_keys(data["yy"])
        cvvElement.send_keys(data["cvv"])
    except Exception as Ex:
        print(Ex)

    cardInfo = {
        "balance": "",
        "status": "",
        "checkresult": ""
    }

    # Get g-response
    response = get_g_response()
    print('G-Captcha: {}'.format(response["g_response"]))
    if response["status"] != 200:
        cardInfo['error'] = 'Can\' resolved captcha'
    else:
        print('Anticaptcha successful.')

    # Inject response in webpage
    try:
        driver.execute_script(
            'document.getElementById("g-recaptcha-response").innerHTML="{}";'.format(response["g_response"]))

        driver.execute_script(
            '___grecaptcha_cfg.clients[0].R.R.callback("{}")'.format(response["g_response"]))

        signInElement.click()

    except Exception as Ex:
        print(Ex)
        response['checkresult'] = 'inject gresponse error'

    # Get card information
    try:
        time.sleep(20)

        avlBalanceElement = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='Avlbal']/div"))
        )

        statusElement = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='brandCardInfo']/div[3]/ul/li[3]/span"))
        )

        avlBalanceValue = avlBalanceElement.text
        statusValue = statusElement.text
        if (avlBalanceValue is not None) and (statusValue is not None):
            cardInfo['checkresult'] = 'OK'

        cardInfo['balance'] = avlBalanceValue
        cardInfo['status'] = statusValue

    except Exception as Ex:
        print(Ex)
        cardInfo['checkresult'] = 'Error'

    # Quit driver and return result
    driver.quit()
    print(cardInfo)

    return cardInfo


    # driver.execute_script(
    #     'const client = ___grecaptcha_cfg.clients[0];' +\
    #     'const keys = Object.keys(client);' +\
    #     'const requiredKey = keys.find(key => client[key].constructor.name === "VK");' +\
    #     'const requiredObj = client[requiredKey];' +\
    #     'const callbackObjKey = Object.keys(requiredObj).find(key => requiredObj[key].callback);' +\
    #     'requiredObj[callbackObjKey].callback("{}");'.format(g_response)
    # )
    # driver.execute_script(
    #     '___grecaptcha_cfg.clients[0].N.N.callback("{}")'.format(g_response))

    # signInElement.click()

    # print('Login successful.')


if __name__ == '__main__':
    app.run(debug=True)
