import json

from tech.mlsql.serviceframework.sdk.app_runtime import AppRuntimeClient, ParamsKey
from tech.mlsql.serviceframework.sdk.plugins.user_system import ArUser


class ArPythonActionNames(object):
    REGISTER = "registerPyAction"
    EXECUTE = "pyAction"
    AUTH = "pyAuthAction"


class ArPythonParamsKey(object):
    RESOURCE_TYPE = "resourceType"
    RESOURCE_NAME = "resourceName"


class ArPythonResourceType(object):
    ADMIN = "admin"
    ACTION = "action"
    CUSTOM = "custom"


class ArPython(object):
    def __init__(self, client: AppRuntimeClient, user: ArUser):
        self.client = client
        self.user = user

    def grant_user(self, auth_user, resource_name, resource_type, revoke=False):
        if revoke:
            raise Exception("not implemented yet")

        params = {ParamsKey.USER_NAME: self.user.user_name,
                  ParamsKey.ACCESS_TOKEN: self.user.token,
                  ArPythonParamsKey.RESOURCE_TYPE: resource_type,
                  ArPythonParamsKey.RESOURCE_NAME: resource_name,
                  "authUser": auth_user}
        r = self.client.request(ArPythonActionNames.AUTH, {**params, **self.client.admin_param()})
        self.client.assert_request(r)
        return r.text

    def grant_user_admin(self, auth_user, revoke=False):
        return self.grant_user(auth_user, "admin", ArPythonResourceType.ADMIN, revoke)

    def grant_user_python_code_execute(self, auth_user, code_name, revoke=False):
        return self.grant_user(auth_user, code_name, ArPythonResourceType.CUSTOM, revoke)

    def grant_user_python_code_register(self, auth_user, revoke=False):
        return self.grant_user(auth_user, ArPythonActionNames.REGISTER, ArPythonResourceType.ACTION, revoke)

    def register_code(self, code_name, code, run_as_admin=False):
        params = {
            ParamsKey.USER_NAME: self.user.user_name,
            ParamsKey.ACCESS_TOKEN: self.user.token,
            "code": code,
            "codeName": code_name
        }
        if run_as_admin:
            params = {**params, **self.client.admin_param()}
        r = self.client.request(ArPythonActionNames.REGISTER, params)
        self.client.assert_request(r)
        return json.loads(r.text)

    def execute_code(self, code_name, run_as_admin=False):
        params = {
            ParamsKey.USER_NAME: self.user.user_name,
            ParamsKey.ACCESS_TOKEN: self.user.token,
            "codeName": code_name
        }
        if run_as_admin:
            params = {**params, **self.client.admin_param()}
        r = self.client.request(ArPythonActionNames.EXECUTE, params)
        self.client.assert_request(r)
        return json.loads(r.text)
