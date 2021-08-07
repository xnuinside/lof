import importlib
import json
from typing import Callable, Dict, List, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse


def create_route(endpoint: Dict, handler: Callable, method: str, app: FastAPI):
    method = getattr(app, method)

    @method(endpoint)
    async def _method(request: Request, response: Response):
        _handler = handler.split(".")
        module = ".".join(_handler[0:-1])
        _handler = _handler[-1]
        my_module = importlib.import_module(module)
        _handler = getattr(my_module, _handler)
        result = _handler(app.event, {})
        status_code = result.get("statusCode") or result.get("status_code") or 200
        if result.get("body"):
            content = result.get("body")
        else:
            content = result
        for header, value in result.get("headers", {}).items():
            response.headers[header] = value
        if status_code == 204:
            response = Response(status_code=status_code)
        else:
            response = JSONResponse(
                content=content, status_code=status_code, headers=response.headers
            )
        return response


def get_query_params(multi_params: Optional[Dict]) -> Dict:
    params = {}
    if multi_params:
        for param in multi_params:
            params[param] = multi_params[param][-1]
        return params


def get_multi_value_params(url: str) -> Dict:
    """extract parmas from url for multiqueryParams"""
    url = str(url).split("/")[-1]
    params = url.split("?")[-1]
    params = params.split("&")
    multi_query_params = {}
    if len(params) == 1:
        params = []
    for param in params:
        name, value = param.split("=")
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
    except Exception:
        pass
    multi_params = get_multi_value_params(request.url)
    headers = {}
    for header in request.headers.items():
        headers[header[0]] = header[1]
    event = {
        "resource": str(request.base_url),
        "path": str(request.url),
        "httpMethod": request.method,
        "requestContext": {
            "resourcePath": "/",
            "httpMethod": request.method,
            "path": str(request.base_url),
        },
        "headers": headers,
        "multiValueHeaders": None,
        "queryStringParameters": get_query_params(multi_params),
        "multiValueQueryStringParameters": multi_params,
        "pathParameters": request.path_params,
        "stageVariables": None,
        "body": json.dumps(body),
        "isBase64Encoded": False,
    }
    return event


def create_middleware(proxy_lambdas: List[Dict], app: FastAPI):
    @app.middleware("http")
    async def lambda_proxy(request: Request, call_next):
        app.event = await prepare_api_gateway_event(request)

        response = None
        for _lambda in proxy_lambdas:
            handler = _lambda["handler"]
            _handler = handler.split(".")
            module = ".".join(_handler[0:-1])
            _handler = _handler[-1]
            my_module = importlib.import_module(module)
            _handler = getattr(my_module, _handler)
            result = _handler(app.event, {})
            if not str(result["statusCode"]).startswith("2"):
                response = Response(status_code=result["statusCode"])
                break
            app.event["requestContext"].update(result["body"])
        else:
            response = await call_next(request)
        return response
