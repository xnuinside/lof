import json

import requests

from tests.utils import LOCAL_ONLY

BASE_URL = "http://localhost:8000"


@LOCAL_ONLY
def test_output_valid_parsing():
    result = requests.get(f"{BASE_URL}/v1/lambda1").text
    expected = {"lambda_result": "bingo"}
    assert json.loads(result) == expected


@LOCAL_ONLY
def test_output_valid_parsing_lambda_with_json_dump():
    result = requests.get(f"{BASE_URL}/v1/lambda3/123").text
    assert json.loads(result)["lambda_event"] is not None
    assert json.loads(result)["lambda_event"]["pathParameters"] == {"someId": "123"}
