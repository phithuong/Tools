from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader

import os
import sys

WRK_DIR = os.path.join(os.path.dirname(__file__), '../')
ACCESS_TOKEN_CONFIG = os.path.join(WRK_DIR, 'config/access_token.json')

sys.path.append(WRK_DIR)
from common.access_token import Token


def home(request):
    token = Token(ACCESS_TOKEN_CONFIG)
    access_token = token.get_access_token_with_kiotviet(token._end_point,
                                                        token._client_id,
                                                        token._client_secret)

    template = loader.get_template('home.html')
    return HttpResponse(template.render())