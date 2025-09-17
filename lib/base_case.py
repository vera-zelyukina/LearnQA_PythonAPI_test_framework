from requests import Response
import json.decoder
from datetime import datetime
import string
import random

class BaseCase:
    def get_cookie (self, response: Response, cookie_name):
        assert cookie_name in response.cookies, f"Cannot find cookie with cookie_name {cookie_name} in the last response"
        return response.cookies[cookie_name]

    def get_header (self, response: Response, header_name):
        assert header_name in response.headers, f"Cannot find cookie with cookie_name {header_name} in the last response"
        return response.headers[header_name]

    def get_json_value(self, response: Response, name):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
            assert False , f"Response is not in JSON format. Response text is '{response.text}'"

        assert name in response_as_dict, f"Response JSON doesn't have key '{name}'"

        return response_as_dict[name]

    def prepare_registration_data(self, email = None):
        if email is None:
            base_part = "learnqa"
            domain = "example.com"
            random_part = datetime.now().strftime("%m%d%Y%H%M%S")
            email = f"{base_part}{random_part}@{domain}"
        return{
            'password': '123',
            'username': 'learnqa',
            'firstName': 'learnqa',
            'lastName': 'learnqa',
            'email': email
        }

    def generate_random_string(self, length=10, punctuation=False, no_digits=False):
        return "".join(
            random.choices(
                string.ascii_uppercase
                + ("" if no_digits else string.digits)
                + (string.punctuation if punctuation else ""),
                k=length,
            )
        )