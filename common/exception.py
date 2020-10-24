class CustomException(Exception):
    def __init__(self, err_code, err_message):
        super().__init__()
        self.err_code = err_code
        self.err_message = err_message

    def get_exception_info(self):
        return {
            'error_code': self.error_code,
            'error_message': self.err_message
        }