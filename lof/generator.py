import importlib
from typing import Any, Callable, Dict, List

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from lof.providers.aws import prepare_api_gateway_event


def create_route(
    endpoint: Dict, handler: Callable, lambda_name: str, method: str, app: FastAPI
):
    method = getattr(app, method)

    @method(endpoint)
    async def _(request: Request, response: Response):
        _handler = handler.split(".")
        module = ".".join(_handler[0:-1])
        _handler = _handler[-1]
        my_module = importlib.import_module(module)
        _handler = getattr(my_module, _handler)

        context = {"function_name": lambda_name}

        app.event["pathParameters"] = request.path_params

        response = prepare_response(
            _handler(app.event, app.context(**context)), response
        )
        return response


def prepare_response(lambda_handler_result: Any, response: Response) -> Response:
    result = lambda_handler_result
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
        if isinstance(content, dict) or isinstance(content, list):
            response = JSONResponse(
                content=content, status_code=status_code, headers=response.headers
            )
        else:
            response = Response(
                content=content, status_code=status_code, headers=response.headers
            )
    return response


def create_middleware(proxy_lambdas: List[Dict], app: FastAPI):
    @app.middleware("http")
    async def _(request: Request, call_next):
        app.event = await prepare_api_gateway_event(request)

        response = None
        for _lambda in proxy_lambdas:
            handler = _lambda["handler"]
            _handler = handler.split(".")
            module = ".".join(_handler[0:-1])
            _handler = _handler[-1]
            my_module = importlib.import_module(module)
            _handler = getattr(my_module, _handler)
            context = {"function_name": _lambda["name"]}

            result = _handler(app.event, app.context(**context))

            if "auth" in _lambda["name"].lower():
                if "context" in result:
                    result.update(result['context'])
                    del result['context']
                    app.event["requestContext"]["authorizer"] = result["context"]
                else:
                    app.event["requestContext"]["authorizer"] = result
            else:
                app.event["requestContext"].update(result)
        else:
            response = await call_next(request)
        return response
