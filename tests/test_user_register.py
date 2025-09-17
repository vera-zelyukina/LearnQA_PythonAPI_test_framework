import pytest
from lib.my_requests import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions

class TestUserRegister(BaseCase):
    exclude_params = [
        "password",
        "email",
        "username",
        "firstName",
        "lastName"
    ]
    def test_create_user_successfully(self):
        data = self.prepare_registration_data()

        response = MyRequests.post('/user/', data=data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

    def test_create_user_with_existing_email(self):
        email = 'vinkotov@example.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post('/user/', data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"Users with email '{email}' already exists", f"Unexpected response content {response.content}"

    def test_create_user_with_invalid_email(self):
        email = 'vinkotovexample.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post('/user/', data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode("utf-8") == f"Invalid email format", f"Unexpected response content {response.content}"

    @pytest.mark.parametrize("condition", exclude_params)
    def test_create_user_without_one_param(self, condition):
        data = self.prepare_registration_data()
        data[condition] = None

        response = MyRequests.post("/user/", data=data)

        Assertions.assert_code_status(response, 400)
        assert response.content.decode(
             "utf-8") == f"The following required params are missed: {condition}", f"Unexpected response content {response.content}"

    def test_create_user_with_short_firstname(self):
        data = self.prepare_registration_data()
        data["firstName"] = self.generate_random_string(1)
        response = MyRequests.post("/user/", data=data)
        Assertions.assert_code_status(response, 400)
        assert response.content.decode(
            "utf-8") == "The value of 'firstName' field is too short", f"Unexpected response content {response.content}"

    def test_create_user_with_too_long_firstname(self):
        data = self.prepare_registration_data()
        data["firstName"] = self.generate_random_string(251)
        response = MyRequests.post("/user/", data=data)
        assert response.content.decode(
            "utf-8") == "The value of 'firstName' field is too long", f"Unexpected response content {response.content}"
