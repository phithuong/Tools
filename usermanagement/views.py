from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

import os
import sys

WRK_DIR = os.path.join(os.path.dirname(__file__), '../')
ACCESS_TOKEN_CONFIG_PATH = os.path.join(WRK_DIR, 'config/access_token.json')
API_LIST_PATH = os.path.join(WRK_DIR, 'config/api_endpoint.json')
APP_CONFIG_PATH = os.path.join(WRK_DIR, 'config/app.json')

sys.path.append(WRK_DIR)
from common.access_token import Token
from common.api import Api
from .forms import LoginForm, UserForm
from .models import User
from common.encryption import Encyption
from common.exception import CustomException
from common.constants import ReturnCode


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            # create a form instance and populate it with data from the request:
            form = LoginForm(request.POST or None, request.FILES or None)
            print(request.POST)

            user_name = request.POST.get('user_name')
            password = request.POST.get('password')

            # Check exists user in db
            user = User.objects.get(user_name=user_name)

            # Check mapping password
            salt = user.salt
            print(salt)
            encyption_info = Encyption.encypt(password, salt)
            if encyption_info['key'] == user.password:
                return redirect('home')

            # # check whether it's valid:
            # if form.is_valid():
            #     # user_name = form.user_name
            #     # password = form.password

            #     # Check exists user in db
            #     user = User.objects.get(user_name=user_name)

            #     # Check mapping password
            #     salt = user.salt
            #     encyption_info = Encyption.encypt(user_name, salt)
            #     if encyption_info['key'] == user.password:
            #         return redirect('home')

            # else:
            #     raise Exception()

        except Exception as Ex:
            return render(request, 'login.html')

    elif request.method == 'GET':
        return render(request, 'login.html')


@csrf_exempt
def regist_user(request):
    if request.method == 'POST':
        try:
            # create a form instance and populate it with data from the request:
            form = UserForm(request.POST or None, request.FILES or None)
            print(request.POST)

            user_name = request.POST.get('user_name')
            password = request.POST.get('password')
            fb_link = request.POST.get('fb_link')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            if age == '':
                age = None
            address = request.POST.get('address')

            try:
                user = User.objects.get(user_name=user_name)
                return render(request, 'regist_user.html')
            except Exception as Ex:
                print('no user')

            # salt = user_name
            salt = user_name
            encyption_info = Encyption.encypt(password, salt)

            user = User(user_name=user_name, password=encyption_info['key'], fb_link=fb_link,
                        gender=gender, age=age, address=address, salt=encyption_info['salt'])
            user.publish()

        except Exception as Ex:
            print(Ex)
            return render(request, 'regist_user.html')

        # check whether it's valid:
        # if form.is_valid():
        #     user_name = form.user_name
        #     password = form.password
        #     fb_link = form.fb_link
        #     gender = form.gender
        #     age = form.age
        #     address = form.address
        #     salt = user_name
        # user = User.objects.get(user_name=user_name)
        # if user:
        #     return render(request, 'regist_user.html')

        # # salt = user_name
        # encyption_info = Encyption.encypt(password, None)

        # user = User(user_name=user_name, password=encyption_info['key'], fb_link=fb_link,
        #             salt=encyption_info['salt'])
        # user.publish()

        # else:
        #     return render(request, 'regist_user.html')

        return redirect('home')

    elif request.method == 'GET':
        return render(request, 'regist_user.html')