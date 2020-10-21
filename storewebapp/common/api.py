import json
import requests

from common.access_token import Token
from common.decorators import Decorators
from common.exception import CustomException
from common.constants import ReturnCode


class Api:
    def __init__(self, token_config_path, api_list_path, retailer, token_type='Bearer'):
        # Get access token
        token = Token(config_file_path=token_config_path)
        self._access_token = token.get_access_token_with_kiotviet()['access_token']

        # Get api list
        self._api_list = Api.get_api_list(api_list_path)

        # Set header of http/https method (call public API)
        self._retailer = retailer
        self._header = {
            'Retailer': retailer,
            'Authorization': '{:s} {:s}'.format(token_type, self._access_token)
        }

    @staticmethod
    def get_api_list(api_list_path):
        api_list = []

        try:
            with open(api_list_path, mode='r') as f:
                api_list = json.load(f)
        except Exception as Ex:
            ex = CustomException(500, ReturnCode.get(500))
            return ex

        return api_list

    @staticmethod
    def call(method, url, headers, payload):
        response = None
        try:
            response = requests.request(method, url, headers = headers, data = payload)
        except Exception as Ex:
            ex = CustomException(500, ReturnCode.get(500))
            return ex

        return response

    # @Decorators.refresh_token
    def get_product_list(self):
        method = self._api_list['GetProductList']['method']
        url = self._api_list['GetProductList']['endpoint']

        payload = {}
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token),
            'Cookie': 'ss-pid=UfGiMD5KsHKOq4wDnSAF; ss-id=MBzimQuGoorIlZCvurlL'
        }

        response = Api.call(method, url, headers, payload)
        print(response.text.encode('utf8'))

    def get_category_list(self):
        method = self._api_list['GetCategoryList']['method']
        url = self._api_list['GetCategoryList']['endpoint']

        payload = {}
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token),
            'Cookie': 'ss-pid=UfGiMD5KsHKOq4wDnSAF; ss-id=MBzimQuGoorIlZCvurlL'
        }
        response = Api.call(method, url, headers, payload)
        print(response.text.encode('utf8'))
