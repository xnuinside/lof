import os
import sys
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI

from lof.code_gen import create_temp_app_folder, generate_app
from lof.env_vars import path_for_env_file, set_env_variables
from lof.errors import NoTemplate, NoVariablesFile
from lof.generator import create_middleware, create_route
from lof.parser import get_endpoints


def validate_paths(template_file: str, variables_file: str) -> None:
    if "/" not in template_file:
        template_file = os.path.join(os.getcwd(), template_file)
    if not os.path.isfile(template_file):
        raise NoTemplate(template_file)

    if variables_file and not os.path.isfile(variables_file):
        raise NoVariablesFile(variables_file)


def add_template_path_to_python_paths(template_file: str, layers: List[str]) -> None:
    lambdas_base_dir = os.path.dirname(template_file)
    sys.path.insert(0, lambdas_base_dir)
    for layer in layers:
        sys.path.insert(0, layer)


def run_fast_api_server(lambdas: List[Dict], proxy_lambdas: List[Dict]) -> FastAPI:

    app = FastAPI()

    create_middleware(proxy_lambdas=proxy_lambdas, app=app)

    for _lambda in lambdas:
        create_route(
            endpoint=_lambda["endpoint"],
            method=_lambda["method"],
            handler=_lambda["handler"],
            app=app,
        )
    return app


def run_multiple_workers_app(
    lambdas: List[Dict],
    port: int,
    host: str,
    workers: int,
    debug: bool,
    reload: bool,
    variables_file: str,
    proxy_lambdas: List[Dict],
) -> None:
    lof_dir = create_temp_app_folder()
    env_file = None
    if variables_file:
        env_file = path_for_env_file(variables_file, lof_dir)
    generate_app(lambdas=lambdas, lof_dir=lof_dir, proxy_lambdas=proxy_lambdas)
    uvicorn.run(
        "lof_app.main:app",
        host=host,
        port=port,
        debug=debug,
        reload=reload,
        env_file=env_file,
        workers=workers,
    )


def runner(
    template_file: str,
    variables_file: Optional[str],
    exclude: Optional[List[str]],
    proxy_lambdas: Optional[List[str]],
    port: Optional[str] = 8000,
    host: Optional[str] = "0.0.0.0",
    workers: Optional[int] = 1,
    debug: Optional[bool] = True,
    reload: Optional[bool] = False,
) -> None:
    if workers <= 0:
        raise ValueError("Count of workers cannot be less when 1")

    validate_paths(template_file, variables_file)
    lambdas, layers, proxy_lambdas = get_endpoints(
        template_file, exclude, proxy_lambdas
    )

    add_template_path_to_python_paths(template_file, layers)

    if variables_file:
        set_env_variables(variables_file)

    if workers == 1 and not reload:

        app = run_fast_api_server(lambdas=lambdas, proxy_lambdas=proxy_lambdas)
        uvicorn.run(app, host=host, port=port, debug=debug)
    else:
        run_multiple_workers_app(
            lambdas=lambdas,
            port=port,
            host=host,
            workers=workers,
            debug=debug,
            reload=reload,
            variables_file=variables_file,
            proxy_lambdas=proxy_lambdas,
        )
