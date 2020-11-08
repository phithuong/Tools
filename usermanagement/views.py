from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

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
from .forms import UserLoginForm, UserRegistForm
from .models import User
from common.encryption import Encyption
from common.exception import CustomException
from common.constants import ReturnCode
from common.session import save_session, get_session

# Read app configuration
app_config = None
with open(APP_CONFIG_PATH, mode='r') as f:
    app_config = json.load(f)
retailer = app_config['retailer']

# Initiate api
api = Api(ACCESS_TOKEN_CONFIG_PATH, API_LIST_PATH, retailer)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            # create a form instance and populate it with data from the request:
            user_form = UserLoginForm(data=request.POST or None, files=request.FILES or None)

            # check whether it's valid:
            # if user_form.is_valid():
            #     user_form = user_form.cleaned_data
            #     user_name = user_form.get('user_name')
            #     password = user_form.get('password')

            data = request.POST
            if ('user_name' in data) and ('password' in data):
                user_name = data.get('user_name')
                password = data.get('password')

                # Check exists user in db
                user = None
                try:
                    user = User.objects.get(user_name=user_name)

                # Case user don't exists
                except ObjectDoesNotExist as Ex:
                    return render(request, 'login.html')

                # Case other exception
                except Exception as Ex:
                    return render(request, 'login.html')

                # Check mapping password
                salt = user.salt
                encyption_info = Encyption.encypt(password, salt)
                if encyption_info['key'] != user.password:
                    raise CustomException(500, 'Password is incorrect.')
                else:
                    user={'user_name': user_name}
                    save_session(request, user=user)
                    response = redirect('home')
                    return response

            else:
                raise CustomException(500, 'Form is invalid.')

        except Exception as Ex:
            response = render(request, 'login.html')
            return response

    elif request.method == 'GET':
        response = render(request, 'login.html')
        return response


@csrf_exempt
def regist_user(request):
    if request.method == 'POST':
        try:
            # create a form instance and populate it with data from the request:
            user_form = UserRegistForm(data=request.POST or None, files=request.FILES or None)

            # Check form is valid
            # if user_form.is_valid():
            #     user_form = user_form.cleaned_data
            #     user_name = user_form.get('user_name')
            #     password = user_form.get('password')
            #     re_password = user_form.get('re_password')
            #     email = user_form.get('email')
            #     fb_link = user_form.get('fb_link', None)

            form_data = request.POST
    
            if ('user_name' in form_data) and ('full_name' in form_data) \
                and ('password' in form_data) and ('re_password' in form_data):
                user_name = form_data.get('user_name')
                full_name = form_data.get('full_name')
                password = form_data.get('password')
                re_password = form_data.get('re_password')
                email = form_data.get('email')
                fb_link = form_data.get('fb_link', None)

                user = None
                try:
                    user = User.objects.get(user_name=user_name)
                except ObjectDoesNotExist as Ex:
                    pass
                else:
                    if user is not None:
                        raise CustomException(500, 'The user is existed.')

                # Regist user to kiotviet
                branches = api.get_branch_list()['data']
                userInfo = api.add_customer(branches[0]['id'], full_name, email=email)['data']

                # salt = user_name
                salt = user_name
                encyption_info = Encyption.encypt(password, salt)

                user = User(user_name=user_name, user_id=userInfo['id'], user_code=userInfo['code'], full_name=full_name,
                            password=encyption_info['key'], email=email, fb_link=fb_link, salt=encyption_info['salt'])
                user.publish()

                user={'user_name': user_name}
                save_session(request, user=user)
                response = redirect('home')
                return response

        except Exception as Ex:
            response = render(request, 'regist_user.html')
            return response

    elif request.method == 'GET':
        response = render(request, 'regist_user.html')
        return response
