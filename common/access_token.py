import json
import requests
from common.exception import CustomException
from common.constants import ReturnCode

class Token:
    def __init__(self, config_file_path=None, access_token_endpoint=None, client_id=None, client_secret=None):
        config = None
        with open(config_file_path) as f:
            config = json.load(f)

        if config is not None:
            self._config = config
            self._access_token_endpoint = config['endpoint']
            self._client_id = config['client_id']
            self._client_secret = config['client_secret']
        else:
            self._config = {
                'endpoint': access_token_endpoint,
                'client_id': client_id,
                'client_secret': client_secret
            }
            self._access_token_endpoint = access_token_endpoint
            self._client_id = client_id
            self._client_secret = client_secret

    def get_settings(self):
        return self._config

    def get_access_token_with_kiotviet(self, access_token_endpoint=None, client_id=None, client_secret=None):
        if access_token_endpoint is None:
            access_token_endpoint = self._access_token_endpoint
            client_id = self._client_id
            client_secret = self._client_secret

        payload = 'scopes=PublicApi.Access.FNB' \
                    + '&grant_type=client_credentials' \
                    + '&client_id={:s}'.format(client_id) \
                    + '&client_secret={:s}'.format(client_secret)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = None

        try:
            response = requests.request("POST", access_token_endpoint, headers=headers, data = payload)
        except Exception as Ex:
            ex = CustomException(500, ReturnCode.get(500))
            return ex
        else:
            response = json.loads(response.text.encode('utf8'))

        return response