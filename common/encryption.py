import os
import hashlib


class Encyption:
    """
    Hash password with sha256 algorithm
    """
    @staticmethod
    def encypt(input_str, salt):
        if salt is None:
            salt = os.urandom(32)
        elif isinstance(salt, str):
            salt = bytearray(salt, 'utf-8')

        key = hashlib.pbkdf2_hmac(
            'sha256', input_str.encode('utf-8'), salt, 100000)
        encyption_info = {
            'salt': salt,
            'key': key
        }
        return encyption_info
