from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader

import os
import sys

WRK_DIR = os.path.join(os.path.dirname(__file__), '../')
ACCESS_TOKEN_CONFIG_PATH = os.path.join(WRK_DIR, 'config/access_token.json')
API_LIST_PATH = os.path.join(WRK_DIR, 'config/api_endpoint.json')
APP_CONFIG_PATH = os.path.join(WRK_DIR, 'config/app.json')

sys.path.append(WRK_DIR)
from common.access_token import Token
from common.api import Api


def home(request):
    api = Api(ACCESS_TOKEN_CONFIG_PATH, API_LIST_PATH, 'kimikids')
    products = api.get_product_list()
    # print(products)

    template = loader.get_template('home.html')
    return HttpResponse(template.render())