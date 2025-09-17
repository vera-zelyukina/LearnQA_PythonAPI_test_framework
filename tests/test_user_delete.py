from lib.my_requests import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions

class TestUserDelete(BaseCase):
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

    def test_delete_user_id_2(self):
        data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
        }
        auth_sid, token = self._login_user(data['email'], data['password'])

        response = MyRequests.delete(
            '/user/2',
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid}
            )

        Assertions.assert_code_status(response, 400)
        assert response.json()['error'] == "Please, do not delete test users with ID 1, 2, 3, 4 or 5.", f"Unexpected response content {response.content}"

    def test_user_create_login_delete(self):
        user = self._register_user()
        user_id = user['user_id']
        auth_sid, token = self._login_user(user['email'], user['password'])

        response1 = MyRequests.delete(
            f'/user/{user_id}',
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            )

        response2 = MyRequests.get(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid}
        )

        Assertions.assert_code_status(response2, 404)
        assert response2.content.decode("utf-8") =='User not found', f"Unexpected response content {response2.content}"

    def test_delete_created_user_by_another_user(self):
        user1 = self._register_user()
        user_id1 = user1['user_id']

        user2 = self._register_user()
        auth_sid2, token2 = self._login_user(user2['email'], user2['password'])

        response = MyRequests.delete(
            f'/user/{user_id1}',
            headers={"x-csrf-token": token2},
            cookies={"auth_sid": auth_sid2},
        )

        Assertions.assert_code_status(response, 400)
        assert response.json().get('error'), f"Unexpected response content {response.content}"

