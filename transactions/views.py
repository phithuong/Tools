from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader

import os
import sys
import json

WRK_DIR = os.path.join(os.path.dirname(__file__), '../')
ACCESS_TOKEN_CONFIG_PATH = os.path.join(WRK_DIR, 'config/access_token.json')
API_LIST_PATH = os.path.join(WRK_DIR, 'config/api_endpoint.json')
APP_CONFIG_PATH = os.path.join(WRK_DIR, 'config/app.json')

sys.path.append(WRK_DIR)
from common.access_token import Token
from common.api import Api


def order(request):
    # Read app configuration
    app_config = None
    with open(APP_CONFIG_PATH, mode='r') as f:
        app_config = json.load(f)
    retailer = app_config['retailer']

    # Initiate api
    api = Api(ACCESS_TOKEN_CONFIG_PATH, API_LIST_PATH, retailer)

    users = api.get_user_list()
    branchs = api.get_branch_list()
    customers = api.get_customer_list()

    print(users)
    print(branchs)
    print(customers)

    return render(request, 'checkout.html')
