import json
from typing import Dict, Optional
from uuid import UUID, uuid4

from fastapi import Request
from pydantic import BaseModel, Field


class Context(BaseModel):

    function_name: str = "MockLambdaName"
    function_version: str = "latest"
    invoked_function_arn: str = "invoked_function_arn"
    memory_limit_in_mb: int = 500
    aws_request_id: UUID = Field(default=str(uuid4()))
    log_group_name: str = "log_group_name"
    log_stream_name: str = "log_stream_name"
    identity: UUID = Field(default=str(uuid4()))
    cognito_identity_id: UUID = Field(default=str(uuid4()))
    cognito_identity_pool_id: UUID = Field(default=str(uuid4()))

    @staticmethod
    def get_remaining_time_in_millis():
        return 4200


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


def get_multi_value_params(url: str) -> Dict:
    """extract parmas from url for multiqueryParams"""
    url = str(url).split("/")[-1]
    base_part = str(url).split("/")[0]
    params = url.split("?")[-1]
    params = params.split("&")
    multi_query_params = {}
    if len(params) == 1 and params[0] == base_part:
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


def get_query_params(multi_params: Optional[Dict]) -> Dict:
    params = {}
    if multi_params:
        for param in multi_params:
            params[param] = multi_params[param][-1]
        return params
