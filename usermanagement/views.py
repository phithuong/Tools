from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

import os
import sys

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


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            # create a form instance and populate it with data from the request:
            user_form = UserLoginForm(data=request.POST or None, files=request.FILES or None)

            # check whether it's valid:
            if user_form.is_valid():
                user_form = user_form.cleaned_data
                user_name = user_form['user_name']
                password = user_form['password']

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
                return render(request, 'login.html')

            save_session(request, user_name=user_name)
            return redirect('home')

        except Exception as Ex:
            return render(request, 'login.html')

    elif request.method == 'GET':
        return render(request, 'login.html')


@csrf_exempt
def regist_user(request):
    if request.method == 'POST':
        try:
            # create a form instance and populate it with data from the request:
            user_form = UserRegistForm(data=request.POST or None, files=request.FILES or None)

            if user_form.is_valid():
                user_form = user_form.cleaned_data
                user_name = user_form.get('user_name')
                password = user_form.get('password')
                email = user_form.get('email')
                fb_link = user_form.get('fb_link', None)

                user = None
                try:
                    user = User.objects.get(user_name=user_name)
                except ObjectDoesNotExist as Ex:
                    pass
                else:
                    if user is not None:
                        return render(request, 'regist_user.html')

                # salt = user_name
                salt = user_name
                encyption_info = Encyption.encypt(password, salt)

                user = User(user_name=user_name, password=encyption_info['key'], email=email,
                            fb_link=fb_link, salt=encyption_info['salt'])
                user.publish()

        except Exception as Ex:
            return render(request, 'regist_user.html')

        save_session(request, user_name=user_name)
        return redirect('home')

    elif request.method == 'GET':
        return render(request, 'regist_user.html')
