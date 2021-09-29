import re
from base64 import b64encode
from hashlib import blake2b
import random
from flask import jsonify

DIGEST_SIZE = 9

regex = re.compile(
    r'^(?:http)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class Shortened:
    def __init__(self):
        self.shortened = {}

    def url_valid(self, url):
        return re.match(regex, url) is not None

    def shorten(self, url):
        url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

        while url_hash in self.shortened:
            url += str(random.randint(0, 9))
            url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

        b64 = b64encode(url_hash.digest(), altchars=b'-_')
        return b64.decode('utf-8')

    def bad_request(self, message):
        response = jsonify({'message': message})
        response.status_code = 400
        return response

    def counter(self, alias):
        return self.shortened[alias]["click_counter"]

    def unique_clicks(self, alias):
        return self.shortened[alias]["unique_counter"]

    def get_countries(self, alias):
        return self.shortened[alias]["countries"]
