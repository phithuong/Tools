from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt

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
from common.session import get_session, save_session

# Read app configuration
app_config = None
with open(APP_CONFIG_PATH, mode='r') as f:
    app_config = json.load(f)
retailer = app_config['retailer']

# Initiate api
api = Api(ACCESS_TOKEN_CONFIG_PATH, API_LIST_PATH, retailer)


def home(request):
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
            'productId': productId,
            'name': product['name'],
            'fullName': product['fullName'],
            'price': product['basePrice'],
            'unit': product['unit'] if 'unit' in product else '',
            'conversionValue': product['conversionValue'] if 'conversionValue' in product else '1'
        }

        # Get inventory
        quantity = 0
        for inventory in product['inventories']:
            if productId == inventory['productId']:
                quantity += inventory['onHand']
        productInfo['inventory'] = quantity

        # Add to list product of category
        data[categoryName].append(productInfo)

    # Save token
    # save_session(request, access_token=api._access_token)

    response = render(request, 'home.html', {'data': data})
    return response


@csrf_exempt
def add_cart(request):
    data = request.POST
    product_id = data.get('productId')

    # Add product to cart
    cart = get_session(request, key='cart')
    if cart is None:
        cart = {
            'total': 0,
            'products': {}
        }
    cart['total'] += 1

    if product_id in cart['products']:
        cart['products'][product_id] += 1
    else:
        cart['products'][product_id] = 1

    # Save cart to session
    save_session(request, cart=cart)

    return JsonResponse({'cart': cart})


def remove_cart(request):
    data = request.POST
    product_id = data.get('productId')

    # Remove product from cart
    cart = get_session(request, key='cart')

    cart['total'] -= 1
    cart['products'][product_id] -= 1

    if cart['products'][product_id] == 0:
        cart['products'].pop(product_id)

    # Save cart to session
    save_session(request, cart=cart)

    response = redirect(reverse('home'))
    return response