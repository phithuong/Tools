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
            if method == 'POST':
                response = requests.request(method, url, headers = headers, data = payload)
            elif method == 'GET':
                response = requests.request(method, url, headers = headers, params = payload)

        except Exception as Ex:
            ex = CustomException(500, ReturnCode.get(500))
            return ex

        return response

    # @Decorators.refresh_token
    def get_product_list(self, currentItem=0, pageSize=20, includeInventory=True):
        method = self._api_list['GetProductList']['method']
        url = self._api_list['GetProductList']['endpoint']

        payload = {'pageSize': pageSize, 'currentItem': currentItem, 'includeInventory': includeInventory}
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token)
        }

        response = Api.call(method, url, headers, payload)
        return response.json()

    def get_category_list(self):
        method = self._api_list['GetCategoryList']['method']
        url = self._api_list['GetCategoryList']['endpoint']

        payload = {}
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token)
        }
        response = Api.call(method, url, headers, payload)
        return response.json()

    def get_user_list(self):
        method = self._api_list['GetUserList']['method']
        url = self._api_list['GetUserList']['endpoint']

        payload = {}
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token)
        }
        response = Api.call(method, url, headers, payload)
        return response.json()

    def get_branch_list(self):
        method = self._api_list['GetBranchList']['method']
        url = self._api_list['GetBranchList']['endpoint']

        payload = {}
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token)
        }
        response = Api.call(method, url, headers, payload)
        return response.json()

    def get_customer_list(self):
        method = self._api_list['GetCustomerList']['method']
        url = self._api_list['GetCustomerList']['endpoint']

        payload = {}
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token)
        }
        response = Api.call(method, url, headers, payload)
        return response.json()

    def add_customer(self, branchId, name, contactNumber='', address='', email=''):
        method = self._api_list['AddCustomerInfo']['method']
        url = self._api_list['AddCustomerInfo']['endpoint']

        payload = {
            'branchId': branchId,
            'name': name,
            'contactNumber': contactNumber,
            'address': address,
            'email': email
        }
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token),
            'Content-Type': 'application/json'
        }
        response = Api.call(method, url, headers, payload)
        return response.json()

    def add_order(self, branchId, casherId, customer, orderDetails, makeInvoice=False):
        method = self._api_list['AddOrder']['method']
        url = self._api_list['AddOrder']['endpoint']

        payload = {
            'branchId': branchId,
            'cashierId': casherId,
            'makeInvoice': False,
            'orderDetails': orderDetails,
            'customer': customer
        }
        headers = {
            'Retailer': self._retailer,
            'Authorization': 'Bearer {:s}'.format(self._access_token),
            'Content-Type': 'application/json'
        }
        response = Api.call(method, url, headers, payload)
        return response.json()
