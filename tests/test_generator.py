import pytest

import lof.generator as g


class MockRequest:
    base_url = "http://localhost"
    url = "http://localhost/lambda?param=1&param1=3&param2=1&param4=5"
    method = "GET"
    path_params = {"a": "a"}
    body = None
    headers = {"header": "header"}


def test_get_multi_value_params():
    expected = {"param1": ["1", "3"], "param2": ["1"], "param4": ["5"]}
    url = "http://localhost/lambda?param1=1&param1=3&param2=1&param4=5"
    assert g.get_multi_value_params(url) == expected


@pytest.mark.asyncio
async def test_prepare_api_gateway_event():
    expected = {
        "resource": "http://localhost",
        "path": "http://localhost/lambda?param=1&param1=3&param2=1&param4=5",
        "httpMethod": "GET",
        "requestContext": {
            "resourcePath": "/",
            "httpMethod": "GET",
            "path": "http://localhost",
        },
        "headers": {"header": "header"},
        "multiValueHeaders": None,
        "queryStringParameters": {
            "param": "1",
            "param1": "3",
            "param2": "1",
            "param4": "5",
        },
        "multiValueQueryStringParameters": {
            "param": ["1"],
            "param1": ["3"],
            "param2": ["1"],
            "param4": ["5"],
        },
        "pathParameters": {"a": "a"},
        "stageVariables": None,
        "body": "null",
        "isBase64Encoded": False,
    }
    assert await g.prepare_api_gateway_event(MockRequest) == expected


def test_get_query_params():
    expected = {"param1": "3", "param2": "1", "param4": "5"}
    multi_param = {"param1": ["1", "3"], "param2": ["1"], "param4": ["5"]}
    assert g.get_query_params(multi_param) == expected
