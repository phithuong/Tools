import json
import requests

class Token:
    def __init__(self, config_file_path):
        config = None
        with open(config_file_path) as f:
            config = json.load(f)

        self._end_point = config['end_point']
        self._client_id = config['client_id']
        self._client_secret = config['client_secret']

    def get_access_token_with_kiotviet(self, end_point, client_id, client_secret):
        payload = 'scopes=PublicApi.Access.FNB' \
                    + '&grant_type=client_credentials' \
                    + '&client_id={:s}'.format(client_id) \
                    + '&client_secret={:s}'.format(client_secret)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", end_point, headers=headers, data = payload)
        response = json.loads(response.text.encode('utf8'))
        return response