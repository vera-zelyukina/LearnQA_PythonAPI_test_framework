from lib.my_requests import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions
import allure

@allure.epic("User")
@allure.feature("Edit user cases")
class TestUserEdit(BaseCase):
    def _register_user(self):
        register_data = self.prepare_registration_data()
        response1 = MyRequests.post('/user/', data=register_data)

        Assertions.assert_code_status(response1, 200)
        Assertions.assert_json_has_key(response1, "id")

        email = register_data['email']
        first_name = register_data['firstName']
        password = register_data['password']
        user_id = self.get_json_value(response1, "id")
        return{'email': email, 'first_name': first_name, 'password':password, 'user_id': user_id}

    def _login_user(self, email, password):
        login_data = {
            'email': email,
            'password': password
        }
        response2 = MyRequests.post('/user/login', data=login_data)

        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")
        return auth_sid, token

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("This test successfully edit user")
    def test_edit_just_created_user(self):
        #REGISTER
        user = self._register_user()

        #LOGIN
        auth_sid, token = self._login_user(user['email'], user['password'])

        #EDIT
        new_name = "Changed Name"

        response3 = MyRequests.put(
            f"/user/{user['user_id']}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={"firstName": new_name}
        )
        Assertions.assert_code_status(response3, 200)

        #GET
        response4 = MyRequests.get(
            f"/user/{user['user_id']}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid}
        )

        Assertions.assert_json_value_by_name(
            response4,
            "firstName",
            new_name,
            "Wrong name of the user after edit"
        )

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("This test checks edit user by unauthorized user")
    def test_edit_created_user_by_user_not_authorize(self):
        user = self._register_user()

        new_name = "Changed Name"

        response3 = MyRequests.put(
            f"/user/{user['user_id']}",
            data={"firstName": new_name}
        )

        Assertions.assert_code_status(response3, 400)
        assert response3.json()['error'] == "Auth token not supplied", f"Unexpected response content {response3.content}"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("This test checks edit user by another user")
    def test_edit_created_user_by_another_user(self):
        user1 = self._register_user()
        user2 = self._register_user()
        auth_sid2, token2 = self._login_user(user2['email'], user2['password'])

        new_name = "Changed Name"

        response3 = MyRequests.put(
            f"/user/{user1['user_id']}",
            headers={"x-csrf-token": token2},
            cookies={"auth_sid": auth_sid2},
            data={"firstName": new_name}
        )

        Assertions.assert_code_status(response3, 400)
        assert response3.json().get('error'), f"Unexpected response content {response3.content}"

    @allure.description("This test checks change the user's email to an incorrect one")
    def test_edit_for_incorrect_email(self):
        #REGISTER
        user = self._register_user()

        #LOGIN
        auth_sid, token = self._login_user(user['email'], user['password'])

        #EDIT
        email = user['email']
        email_without_at = email.replace("@", "")

        response3 = MyRequests.put(
            f"/user/{user['user_id']}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={"email": email_without_at}
        )

        Assertions.assert_code_status(response3, 400)
        assert response3.json()['error'] == "Invalid email format", f"Unexpected response content {response3.content}"

    @allure.description("This test checks change the user's first name to too short one")
    def test_edit_too_short_firstname(self):
        #REGISTER
        user = self._register_user()

        #LOGIN
        auth_sid, token = self._login_user(user['email'], user['password'])

        #EDIT
        new_name = self.generate_random_string(1)

        response3 = MyRequests.put(
            f"/user/{user['user_id']}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={"firstName": new_name}
        )

        Assertions.assert_code_status(response3, 400)
        assert response3.json()['error'] == "The value for field `firstName` is too short", f"Unexpected response content {response3.content}"