class Api:
    def __init__(self, retailer, authorization, token_type='Bearer'):
        self._retailer = retailer
        self._authorization = authorization
        self._header = {
            'Retailer': retailer,
            'Authorization': '{:s} {:s}'.format(token_type, authorization)
        }