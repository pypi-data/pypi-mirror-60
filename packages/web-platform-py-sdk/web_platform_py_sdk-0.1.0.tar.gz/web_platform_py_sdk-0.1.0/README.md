# web_platform_py_sdk

```python
from tech.mlsql.serviceframework.sdk.app_runtime import AppRuntimeClient
from tech.mlsql.serviceframework.sdk.plugins.ar_python import ArPython
from tech.mlsql.serviceframework.sdk.plugins.user_system import ArUser

# create the container client
client = AppRuntimeClient("admin", "http://127.0.0.1:9007/run")

# for user plugin
user_client = ArUser(client)
user_client.login("jack", "123")

# for python plugin 
python_client = ArPython(client, user_client)

# grant code register for user jack
python_client.grant_user_python_code_register("jack")
# grant execution for user jack
python_client.grant_user_python_code_execute("jack", "echo")

python_code = """from pyjava.api.mlsql import PythonContext
for row in context.fetch_once():
    print(row)
context.build_result([{"content": "{}"}], 1)
    """
# register code
python_client.register_code("echo", python_code)

# execute the python code
python_client.execute_code("echo")

```