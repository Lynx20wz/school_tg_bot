import requests


class Auth:
    def __init__(self, token):
        self.token = token

    def get_info(self):
        headers = {
            "partner-source-id": "MOBILE"
        },
        response = requests.get('https://myschool.mosreg.ru/acl/api/users/profile_info', headers=headers)
        return response.json()
