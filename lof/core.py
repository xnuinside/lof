import json
import os
import sys
from typing import Dict, List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from lof.errors import NoTemplate, NoVariablesFile
from lof.parser import get_endpoints
from lof.generator import create_route


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


def validate_paths(template_file: str, variables_file: str):
    if "/" not in template_file:
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
    template_file: str, exclude: List[str], variables_file: Optional[str] = None
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
        template_file=template_file, variables_file=variables_file, exclude=exclude
    )
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
