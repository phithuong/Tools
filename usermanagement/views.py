import os
import sys
import json

WRK_DIR = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(WRK_DIR)

from .models import User
from common.encryption import Encyption
from common.exception import CustomException
from common.constants import ReturnCode
from common.session import save_session, get_session, remove_session

from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.models import SocialAccount

from common.view_base import ViewBase
view_base = ViewBase()
api = view_base.get_api_instance()
messages = view_base.get_messages()


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
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
                    raise CustomException(500, messages['business_error']['username_incorrect'])

                # Check mapping password
                salt = user.salt
                encyption_info = Encyption.encypt(password, salt)
                if encyption_info['key'] != user.password:
                    raise CustomException(500, messages['business_error']['password_incorrect'])
                else:
                    userKiotviet = api.get_customer_detail(user.user_id)

                    user={'user_name': user_name, 'user_id': userKiotviet['id']}
                    save_session(request, user=user)
                    response = redirect('home')
                    return response

            else:
                raise CustomException(500, messages['business_error']['input_not_enough'])

        except CustomException as Ex:
            response = render(request, 'login.html', {'error_message': Ex.err_message})
            return response

        except Exception as Ex:
            error_message = messages['system_error']['general_system_error']
            response = render(request, 'regist_user.html', {'error_message': error_message})
            return response

    elif request.method == 'GET':
        response = render(request, 'login.html', {'error_message': ''})
        return response


@csrf_exempt
def logout(request):
    remove_session(request, key='user')
    response = redirect('home')
    return response


@csrf_exempt
def fb_login(request):
    user = request.user
    user_name = user.username
    email = user.email
    full_name = '{} {}'.format(user.first_name, user.last_name)
    password = user.password
    uid = SocialAccount.objects.filter(user=user)[0].uid
    fb_link = 'https://facebook.com/{}'.format(uid)

    userDb = None
    userKiotviet = None
    try:
        userDb = User.objects.get(user_name=user_name)
    except ObjectDoesNotExist as Ex:

        # Regist user to kiotviet
        branches = api.get_branch_list()['data']
        userKiotviet = api.add_customer(branches[0]['id'], full_name, email=email)['data']

        userDb = User(user_name=user_name, user_id=userKiotviet['id'], user_code=userKiotviet['code'],
                      full_name=full_name, password=None, email=email, fb_link=fb_link, salt=None)
        userDb.publish()

    else:
        if userDb is not None:
            userKiotviet = api.get_customer_detail(userDb.user_id)

    user={'user_name': user_name, 'user_id': userKiotviet['id'], 'fb_link': fb_link}
    save_session(request, user=user)
    response = redirect('home')
    return response


@csrf_exempt
def fb_logout(request):
    remove_session(request, key='user')
    response = redirect('home')
    return response


@csrf_exempt
def regist_user(request):
    if request.method == 'POST':
        try:
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
                        raise CustomException(500, messages['business_error']['username_duplicate'])

                try:
                    user = User.objects.get(email=email)
                except ObjectDoesNotExist as Ex:
                    pass
                else:
                    if user is not None:
                        raise CustomException(500, messages['business_error']['email_duplicate'])

                if (password != re_password):
                    raise CustomException(500, messages['business_error']['confirm_password_mismatch'])

                # Regist user to kiotviet
                branches = api.get_branch_list()['data']
                userKiotviet = api.add_customer(branches[0]['id'], full_name, email=email)['data']

                # salt = user_name
                salt = user_name
                encyption_info = Encyption.encypt(password, salt)

                user = User(user_name=user_name, user_id=userKiotviet['id'], user_code=userKiotviet['code'], full_name=full_name,
                            password=encyption_info['key'], email=email, fb_link=fb_link, salt=encyption_info['salt'])
                user.publish()

                user={'user_name': user_name, 'user_id': userKiotviet['id'], 'fb_link': fb_link}
                save_session(request, user=user)
                response = redirect('home')
                return response

        except CustomException as Ex:
            response = render(request, 'regist_user.html', {'error_message': Ex.err_message})
            return response

        except Exception as Ex:
            error_message = messages['system_error']['general_system_error']
            response = render(request, 'regist_user.html', {'error_message': error_message})
            return response

    elif request.method == 'GET':
        response = render(request, 'regist_user.html')
        return response
