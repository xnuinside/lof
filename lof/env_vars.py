import json
import os
from typing import Dict

from dotenv import load_dotenv


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


def path_for_env_file(variables_file: str, lof_dir: str) -> str:
    file_path = variables_file
    if variables_file.endswith(".json"):
        file_path = create_temp_env_file(file_path, lof_dir)
    return file_path


def create_temp_env_file(variables_file: str, lof_dir: str) -> str:
    target_path = os.path.join(lof_dir, ".env")
    variables = get_variables(variables_file)
    variables_txt = "".join([f"{name}={value}\n" for name, value in variables.items()])
    with open(target_path, "w+") as env_file:
        env_file.write(variables_txt)
    return target_path
