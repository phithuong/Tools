import os
import sys
import json
import re

from common.session import get_session, save_session
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt

from common.view_base import ViewBase
view_base = ViewBase()
api = view_base.get_api_instance()
messages = view_base.get_messages()


def home(request, p=''):
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
    products_info = api.get_product_list(
        currentItem=current_item, pageSize=page_size)
    products = products_info['data']
    total_product = products_info['total']

    loop = ((total_product - page_size) // page_size) + 1
    for ii in range(loop):
        current_item += page_size

        if (ii == loop - 1):
            page_size = total_product - current_item

        next_products = api.get_product_list(
            currentItem=current_item, pageSize=page_size)['data']
        products.extend(next_products)

    # Inventory information (productId : quantity)
    inventoryInfos = {}

    # Get cart information
    cart = get_session(request, key='cart')

    for product in products:
        categoryName = product['categoryName']

        categoryId = product['categoryId']
        productId = product['id']

        # search text
        isNotFound = True
        if (re.search(p, categoryName, re.IGNORECASE) is not None) \
            or (re.search(p, product['name'], re.IGNORECASE) is not None) \
            or (re.search(p, product['fullName'], re.IGNORECASE) is not None):
            isNotFound = False

        if isNotFound:
            continue

        if (cart is not None) and str(productId) in cart['products']:
            orderQuantity = cart['products'][str(productId)]
        else:
            orderQuantity = 0

        # Add product
        productInfo = {
            'productId': productId,
            'name': product['name'],
            'fullName': product['fullName'],
            'price': product['basePrice'],
            'unit': product['unit'] if 'unit' in product else '',
            'conversionValue': product['conversionValue'] if 'conversionValue' in product else '1',
            'orderQuantity': orderQuantity
        }

        # Get inventory
        quantity = 0
        for inventory in product['inventories']:
            if productId == inventory['productId']:
                quantity += inventory['onHand']
        productInfo['inventory'] = quantity

        # Add to list product of category
        data[categoryName].append(productInfo)

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

    response = JsonResponse({'cart': cart})
    return response


@csrf_exempt
def remove_cart(request):
    data = request.POST
    product_id = data.get('productId')
    is_subtract = data.get('isSubtract')

    # Remove product from cart
    cart = get_session(request, key='cart')

    cart['total'] -= 1
    if product_id in cart['products']:
        if is_subtract:
            cart['products'][product_id] -= 1
        else:
            cart['products'][product_id] = 0

    if cart['products'][product_id] == 0:
        cart['products'].pop(product_id)

    # Save cart to session
    save_session(request, cart=cart)

    response = JsonResponse({'cart': cart})
    return response
