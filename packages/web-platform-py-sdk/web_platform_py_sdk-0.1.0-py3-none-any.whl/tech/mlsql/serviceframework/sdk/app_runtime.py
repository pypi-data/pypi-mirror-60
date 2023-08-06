import json

import requests


class ParamsKey(object):
    ACCESS_TOKEN = "access-token"
    USER_NAME = "userName"
    PASSWORD = "password"
    ACTION = "action"
    ADMIN_TOKEN = "admin_token"


class Action(object):
    CONTROL_REG = "controlReg"
    ADD_DB = "addDB"
    ADD_PLUGIN_INSTANCE_ADDRESS = "addProxy"


class DBConfig(object):
    def __init__(self, db_name, db_host, db_port, db_user, db_password):
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password


class AppRuntimeClient(object):
    def __init__(self, admin_token, instance_url):
        self.admin_token = admin_token
        self.instance_url = instance_url

    def request(self, action, params):
        r = requests.post(self.instance_url, {**params, **{ParamsKey.ACTION: action}})
        return r

    def assert_request(self, r):
        if r.status_code != 200:
            raise Exception(r.text)

    def admin_param(self):
        return {ParamsKey.ADMIN_TOKEN: self.admin_token}


class AppSystem(object):

    def __init__(self, client: AppRuntimeClient):
        self.client = client

    def admin_param(self):
        return self.client.admin_param()

    def enable_user_reg(self):
        r = self.client.request(Action.CONTROL_REG, {
            **self.admin_param(), **{"enable": "true"}
        })
        self.client.assert_request(r)
        return json.loads(r.text)

    def disable_user_reg(self):
        r = self.client.request(Action.CONTROL_REG, {
            **self.admin_param(), **{"enable": "false"}
        })
        self.client.assert_request(r)
        return json.loads(r.text)

    def add_db_for_plugin(self, plugin_name, db_config: DBConfig):
        def db_config_template(db_config: DBConfig):
            return """
        {}:
              host: {}
              port: {}
              database: {}
              username: {}
              password: {}
              initialSize: 8
              disable: true
              removeAbandoned: true
              testWhileIdle: true
              removeAbandonedTimeout: 30
              maxWait: 100
              filters: stat,log4j
        """.format(db_config.db_name,
                   db_config.db_host,
                   db_config.db_port,
                   db_config.db_name,
                   db_config.db_user,
                   db_config.db_password)

        params = {"dbName": db_config.db_name, "instanceName": plugin_name,
                  "dbConfig": db_config_template(db_config)}
        r = self.client.request(Action.ADD_DB, {**params, **self.admin_param()})
        self.client.assert_request(r)
        return json.loads(r.text)

    def add_plugin_instance_address(self, name, value):
        params = {"name": name, "value": value}
        r = self.client.request(Action.ADD_PLUGIN_INSTANCE_ADDRESS, {**params, **self.client.admin_token})
        self.client.assert_request(r)
        return json.loads(r.text)
