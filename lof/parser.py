import json
import os
from typing import Dict, List, TextIO, Tuple

import yaml


def _get_format(template_file: str) -> str:
    _, extension = os.path.splitext(template_file)
    return extension.lower()[1:]


def _parse_template(content: TextIO, format_name: str) -> Dict:
    yaml.add_multi_constructor("", any_constructor, Loader=yaml.SafeLoader)
    if format_name in ["yml", "yaml"]:
        return yaml.safe_load(content)
    if format_name == "json":
        return json.load(content)


def any_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)


def get_endpoints(
    template_file: str, exclude: List[str], proxy_lambdas: List[str]
) -> Tuple[List[Dict], List[str]]:
    """parse Cloud Fomation Template to extract info about lambdas"""
    _resources = {}
    layers = []

    with open(template_file, "r") as tf:
        format_name = _get_format(template_file)
        template = _parse_template(tf, format_name)
        resources = template["Resources"]
        for resource, resource_data in resources.items():
            if "AWS::Serverless::Function" in resource_data["Type"]:
                _resources[resource] = resource_data
            elif "AWS::Serverless::LayerVersion" in resource_data["Type"]:
                layers.append(resource_data["Properties"]["ContentUri"])

    lambdas, proxy_lambdas = process_lambdas_resources(
        _resources, exclude, proxy_lambdas
    )

    return lambdas, layers, proxy_lambdas


def process_lambdas_resources(
    resources: Dict, exclude: List[str], proxy_lambdas: List[str]
) -> List[Dict]:
    lambdas = []
    p_lambdas = []
    for lambda_name, data in resources.items():
        if lambda_name not in exclude:
            code_uri = data["Properties"]["CodeUri"].replace("/", ".")
            if not code_uri.endswith("."):
                code_uri += "."
            handler = f"{code_uri}{data['Properties']['Handler']}"
            events = data["Properties"].get("Events")
            if lambda_name in proxy_lambdas:
                p_lambdas.append({"name": lambda_name, "handler": handler})
                continue
            if not events:
                # mean it is authorizer or smth relative
                continue
            lambdas.extend(get_lambdas_endpoints(events, lambda_name, handler))
    return lambdas, p_lambdas


def get_lambdas_endpoints(
    events: Dict, lambda_name: str, handler_str: str
) -> List[Dict]:
    endpoints = []
    for _, event in events.items():
        _type = event["Type"]
        if _type != "Api":
            continue
        method = event["Properties"]["Method"].lower()
        if method == "options":
            # this is for CORS, we not insteresting
            continue
        endpoint_info = {
            "name": lambda_name,
            "method": method,
            "endpoint": event["Properties"]["Path"],
            "handler": handler_str,
        }
        endpoints.append(endpoint_info)
    return endpoints
