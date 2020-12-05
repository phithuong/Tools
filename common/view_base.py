import os
import sys
import json

WRK_DIR = os.path.join(os.path.dirname(__file__), '../')

sys.path.append(WRK_DIR)
from common.access_token import Token
from common.api import Api


class ViewBase:
    ACCESS_TOKEN_CONFIG_PATH = os.path.join(WRK_DIR, 'config/access_token.json')
    API_LIST_PATH = os.path.join(WRK_DIR, 'config/api_endpoint.json')
    APP_CONFIG_PATH = os.path.join(WRK_DIR, 'config/app.json')
    MESSAGE_LIST_PATH = os.path.join(WRK_DIR, 'config/message.json')

    def __init__(self):
        self._access_token_config = ViewBase._read_json(ViewBase.ACCESS_TOKEN_CONFIG_PATH)
        self._app_config = ViewBase._read_json(ViewBase.APP_CONFIG_PATH)
        self._api = Api(ViewBase.ACCESS_TOKEN_CONFIG_PATH,
                        ViewBase.API_LIST_PATH,
                        self._app_config['retailer'])
        self._messages = ViewBase._read_json(ViewBase.MESSAGE_LIST_PATH)

    def get_api_instance(self):
        return self._api

    def get_messages(self):
        return self._messages

    @staticmethod
    def _read_json(file_path):
        with open(file_path, mode='r', encoding='utf-8') as f:
            return json.load(f)