import importlib
import json
import os
import sys
from collections import defaultdict
from typing import Callable, Dict, List, Optional

import uvicorn
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from lof.errors import NoTemplate, NoVariablesFile


def set_env_variables(variables_file: str):
    if os.path.basename(variables_file).endswith(".json"):
        variables = get_variables(variables_file)
        if "Parameters" in variables:
            variables = variables["Parameters"]
        for variable, value in variables.items():
            os.environ[variable] = value
    elif os.path.basename(variables_file).startswith("."):
        load_dotenv(variables_file)


def get_variables(variables_file: str) -> Dict:
    if os.path.basename(variables_file).endswith(".json"):
        with open(variables_file, "r") as vf:
            variables = json.load(vf)
            return variables


def any_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)


def get_endpoints(temaplte_file: str) -> List[Dict]:

    _resources = {}
    layers = []
    yaml.add_multi_constructor("", any_constructor, Loader=yaml.SafeLoader)
    with open(temaplte_file, "r") as tf:
        template = yaml.safe_load(tf)
        resources = template["Resources"]
        for resource, resource_data in resources.items():
            if "AWS::Serverless::Function" in resource_data["Type"]:
                _resources[resource] = resource_data
            elif "AWS::Serverless::LayerVersion" in resource_data["Type"]:
                layers.append(resource_data["Properties"]["ContentUri"])

    lambdas = []

    for lambda_name, data in _resources.items():
        code_uri = data["Properties"]["CodeUri"].replace("/", ".")
        if not code_uri.endswith("."):
            code_uri += "."
        handler = f"{code_uri}{data['Properties']['Handler']}"
        events = data["Properties"].get("Events")
        if not events:
            # mean it is authorizer or smth relative
            continue
        for _, event in events.items():
            method = event["Properties"]["Method"].lower()
            if method == "options":
                # this is for CORS, we not insteresting
                continue
            _lambda = {
                "name": lambda_name,
                "method": method,
                "endpoint": event["Properties"]["Path"],
                "handler": handler,
            }
            lambdas.append(_lambda)
    return lambdas, layers


def create_route(endpoint: Dict, handler: Callable, method: str, app: FastAPI):
    method = getattr(app, method)

    @method(endpoint)
    async def _method(request: Request):
        _handler = handler.split(".")
        module = ".".join(_handler[0:-1])
        _handler = _handler[-1]
        my_module = importlib.import_module(module)
        _handler = getattr(my_module, _handler)
        event = await prepare_api_gateway_event(request)
        return _handler(event, {})


def get_multi_value_params(url: str) -> Dict:
    dir(url)
    url = str(url).split("/")[-1]
    params = url.split("?")[-1]
    params = params.split("&")
    multi_query_params = {}
    if len(params) == 1: 
        params = []
    for param in params:
        name, value = param.split('=')
        if not multi_query_params.get(name):
            multi_query_params[name] = [value]
        else:
            multi_query_params[name].append(value)
    if not multi_query_params:
        multi_query_params = None
    return multi_query_params


async def prepare_api_gateway_event(request: Request) -> Request:
    body = None
    try:
         body = await request.json()
    except:
        pass
    event = {
        "resource": request.base_url,
        "path": request.url,
        "httpMethod": request.method,
        "requestContext": {
            "resourcePath": "/",
            "httpMethod": request.method,
            "path": request.base_url,
        },
        "headers": request.headers,
        "multiValueHeaders": None,
        "queryStringParameters": request._query_params,
        "multiValueQueryStringParameters": get_multi_value_params(request.url),
        "pathParameters": request.path_params,
        "stageVariables": None,
        "body": body,
        "isBase64Encoded": False,
    }
    return event


def validate_paths(template_file: str, variables_file: str):
    if not "/" in template_file:
        template_file = os.path.join(os.getcwd(), template_file)
    if not os.path.isfile(template_file):
        raise NoTemplate(template_file)

    if variables_file and not os.path.isfile(variables_file):
        raise NoVariablesFile(variables_file)


def add_template_path_to_python_paths(template_file, layers):
    lambdas_base_dir = os.path.dirname(template_file)
    sys.path.insert(0, lambdas_base_dir)
    for layer in layers:
        sys.path.insert(0, layer)


def run_fast_api_server(
    template_file: str, 
    exclude: List[str], 
    variables_file: Optional[str] = None
) -> FastAPI:
    validate_paths(template_file, variables_file)

    lambdas, layers = get_endpoints(template_file)
    add_template_path_to_python_paths(template_file, layers)
    if variables_file:
        set_env_variables(variables_file)

    app = FastAPI()

    for _lambda in lambdas:
        if _lambda["name"] not in exclude:
            create_route(
                endpoint=_lambda["endpoint"],
                method=_lambda["method"],
                handler=_lambda["handler"],
                app=app,
            )
    return app


def runner(
    template_file: str, variables_file: Optional[str], exclude: Optional[List[str]]
) -> None:

    app = run_fast_api_server(
        template_file=template_file,
        variables_file=variables_file,
        exclude=exclude)
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
