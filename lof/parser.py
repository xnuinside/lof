from typing import Dict, List

import yaml


def any_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)


def get_endpoints(temaplte_file: str) -> List[Dict]:
    """parse Cloud Fomation Template to extract info about lambdas"""
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

    lambdas = process_lambdas_resources(_resources)

    return lambdas, layers


def process_lambdas_resources(resources: Dict) -> List[Dict]:
    lambdas = []
    for lambda_name, data in resources.items():
        code_uri = data["Properties"]["CodeUri"].replace("/", ".")
        if not code_uri.endswith("."):
            code_uri += "."
        handler = f"{code_uri}{data['Properties']['Handler']}"
        events = data["Properties"].get("Events")
        if not events:
            # mean it is authorizer or smth relative
            continue
        lambdas.extend(get_lambdas_endpoints(events, lambda_name, handler))
    return lambdas


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
