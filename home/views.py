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
from common.session import get_session


def home(request):
    # Read app configuration
    app_config = None
    with open(APP_CONFIG_PATH, mode='r') as f:
        app_config = json.load(f)
    retailer = app_config['retailer']

    # Initiate api
    api = Api(ACCESS_TOKEN_CONFIG_PATH, API_LIST_PATH, retailer)

    data = {}
    current_item = 0
    page_size = 20

    # Get categories
    categories = api.get_category_list()['data']
    category_ids = []
    category_names = []
    for category in categories:
        category_ids.append(category['categoryId'])
        category_names.append(category['categoryName'])
        data[category['categoryName']] = []

    # Get products
    products_info = api.get_product_list(currentItem=current_item, pageSize=page_size)
    products = products_info['data']
    total_product = products_info['total']

    loop = ((total_product - page_size) // page_size) + 1
    for ii in range(loop):
        current_item += page_size

        if (ii == loop - 1):
            page_size = total_product - current_item

        next_products = api.get_product_list(currentItem=current_item, pageSize=page_size)['data']
        products.extend(next_products)

    # Inventory information (productId : quantity)
    inventoryInfos = {}

    for product in products:
        categoryName = product['categoryName']

        categoryId = product['categoryId']
        productId = product['id']

        productInfo = {
            'id': productId,
            'name': product['name'],
            'fullName': product['fullName'],
            'price': product['basePrice'],
            'unit': product['unit'] if 'unit' in product else '1',
            'conversionValue': product['conversionValue']
        }

        # Get inventory
        quantity = 0
        for inventory in product['inventories']:
            if productId == inventory['productId']:
                quantity += inventory['onHand']
        productInfo['inventory'] = quantity

        # Add to list product of category
        data[categoryName].append(productInfo)

    # Get user name
    user_name = get_session(request, 'user_name')

    response = render(request, 'home.html', {'data': data, 'user_name': user_name})
    return response