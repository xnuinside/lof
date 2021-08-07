import os
import sys
from typing import Dict, List

from jinja2 import Template

LOF_DIR = ".lof"

route_template = """
@app.{method}("{endpoint}")
async def {function_name}(request: Request, response: Response):
    my_module = importlib.import_module("{module}")
    _handler = getattr(my_module, "{handler}")
    result = _handler(app.event, app.context(function_name="{lambda_name}"))
    status_code = result.get("statusCode") or result.get("status_code") or 200
    if result.get("body"):
        content = result.get("body")
    else:
        content = result
    for header, value in result.get("headers", {{}}).items():
        response.headers[header] = value
    if status_code == 204:
        response = Response(status_code=status_code)
    else:
        response = JSONResponse(
            content=content, status_code=status_code, headers=response.headers
        )
    return response
"""


def create_temp_app_folder() -> str:
    lof_path = os.path.join(os.getcwd(), LOF_DIR)
    os.makedirs(lof_path, exist_ok=True)
    lof_app = os.path.join(lof_path, "lof_app")
    os.makedirs(lof_app, exist_ok=True)
    sys.path.insert(0, lof_path)
    return lof_path


def get_function_name(method: str, endpoint: str) -> str:
    endpoint_name = endpoint.split("{")[0]
    for symbol in ["/", "-", "&", "$", "%", "."]:
        endpoint_name = endpoint_name.replace(symbol, "_")
    return f"{method}_{endpoint_name}"


def create_route(endpoint: str, method: str, handler: str, lambda_name: str) -> str:

    _handler = handler.split(".")
    module = ".".join(_handler[0:-1])
    _handler = _handler[-1]
    function_name = get_function_name(method, endpoint)

    return route_template.format(
        function_name=function_name,
        endpoint=endpoint,
        method=method,
        module=module,
        handler=_handler,
        lambda_name=lambda_name,
    )


def get_routes(lambdas: List[Dict]) -> List[str]:
    routes = []
    for _lambda in lambdas:
        route = create_route(
            endpoint=_lambda["endpoint"],
            method=_lambda["method"],
            handler=_lambda["handler"],
            lambda_name=_lambda["name"],
        )
        routes.append(route)
    return routes


def render_app_template(lambdas: List[Dict], proxy_lambdas: List[Dict]) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, "template.jinja2")
    with open(template_path) as file_:
        template = Template(file_.read())
    app_routes = get_routes(lambdas)
    app_code = template.render({"routes": app_routes, "proxy_lambdas": proxy_lambdas})
    return app_code


def save_app_code(app_code, lof_dir) -> None:
    with open(os.path.join(lof_dir, "lof_app", "main.py"), "w+") as main_module:
        main_module.write(app_code)


def generate_app(lambdas: List[Dict], lof_dir: str, proxy_lambdas: List[Dict]) -> str:
    app_code = render_app_template(lambdas, proxy_lambdas)
    save_app_code(app_code, lof_dir)
