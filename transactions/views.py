import os
import sys
import json

WRK_DIR = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(WRK_DIR)

from common.session import get_session, save_session, remove_session
from usermanagement.models import User

from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader

from common.view_base import ViewBase
view_base = ViewBase()
api = view_base.get_api_instance()
messages = view_base.get_messages()

NO_PRODUCT_IN_CART_MESSAGE = 'Giỏ hàng của bạn chưa có sản phẩm nào'
ORDER_SUCCESS_MESSAGE = 'Đặt hàng thành công'


def order(request):
    if request.method == 'GET':

        # Get user information
        user = get_session(request, key='user')
        if user is None:
            return redirect('login')

        fb_link = user['fb_link']

        user_info = {}
        if user is not None:
            user_kiotviet = api.get_customer_detail(user['user_id'])
            user_info = {
                'fullName': user_kiotviet['name'],
                'email': user_kiotviet['email'],
                'contactNumber': user_kiotviet['contactNumber'],
                'address': user_kiotviet['address']
            }

        # Get cart detail
        cart = get_session(request, key='cart')
        if cart is None:
            response = render(request, 'checkout_info.html', {'message': NO_PRODUCT_IN_CART_MESSAGE})
            return response

        data = {}
        for productId in cart['products'].keys():
            productDetail = api.get_product_detail(productId)

            productInfo = {
                'name': productDetail['name'],
                'fullName': productDetail['fullName'],
                'price': productDetail['basePrice'],
                'unit': productDetail['unit'] if 'unit' in productDetail else '',
                'conversionValue': productDetail['conversionValue'] if 'conversionValue' in productDetail else '1',
                'inventories': productDetail['inventories']
            }

            if productId not in data:
                data[productId] = {
                    'productName': productDetail['name'],
                    'productUnit': productInfo['unit'],
                    'productNum': cart['products'][productId],
                    'productPrice': productDetail['basePrice']
                }

        response = render(request, 'checkout.html', {'data': data, 'user': user_info})
        return response

    elif request.method == 'POST':

        # Get order detail
        data = request.POST

        full_name = data.get('receiver-name')
        email = data.get('email')
        phone_number = data.get('tele-phone')
        zipcode = data.get('zipcode')
        address = data.get('address')
        note = data.get('note')
        payment_type = data.get('choice-payments')
        bank_cardnum = data.get('bank-account-number')
        ship_type = data.get('choice-ship')

        # Get user and branch
        users = api.get_user_list()['data']
        branches = api.get_branch_list()['data']

        # Get cart detail
        cart = get_session(request, key='cart')
        orderInfo = []

        for productId in cart['products'].keys():
            productDetail = api.get_product_detail(productId)

            productInfo = {
                'productId': productDetail['id'],
                'productCode': productDetail['code'],
                'productName': productDetail['name'],
                'quantity': cart['products'][productId],
                'price': productDetail['basePrice'],
                'discount': 0
            }
            orderInfo.append(productInfo)

        user = get_session(request, key='user')
        fb_link = user['fb_link']

        customerInfo = {
            "name": full_name,
            "contactNumber": phone_number,
            "address": address,
            "email": email,
            "comment": '{}\n{}'.format(note, fb_link)
        }

        branchId = branches[0]['id']
        cashierId = users[0]['id']
        description = '{}\n{}'.format(note, fb_link)

        order_response = api.add_order(branchId, cashierId, description, customerInfo, orderInfo)
        remove_session(request, key='cart')

        response = render(request, 'checkout_info.html', {'message': ORDER_SUCCESS_MESSAGE})
        return response
