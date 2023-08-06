import json

from tech.mlsql.serviceframework.sdk.app_runtime import AppRuntimeClient, ParamsKey


class ArUserActionNames(object):
    USER_LOGIN = "userLogin"
    USER_REG = "userReg"


class ArUser(object):

    def __init__(self, client: AppRuntimeClient):
        self.client = client
        self.token = None
        self.user_name = None
        self.password = None

    def reg_user(self, user_name, password):
        r = self.client.request(ArUserActionNames.USER_REG,
                                {ParamsKey.USER_NAME: user_name, ParamsKey.PASSWORD: password})
        self.client.assert_request(r)
        return json.loads(r.text)

    def login(self, user_name, password):
        r = self.client.request(ArUserActionNames.USER_LOGIN,
                                {ParamsKey.USER_NAME: user_name, ParamsKey.PASSWORD: password})
        token_col = json.loads(r.text)
        if len(token_col) == 1:
            self.token = token_col[0]['token']
            self.user_name = user_name
            self.password = password
        return self.token

    def logout(self):
        self.token = None
        self.user_name = None
        self.password = None
