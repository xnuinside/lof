import yaml
from typing import List, Dict


def any_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)


def get_endpoints(temaplte_file: str) -> List[Dict]:

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

    lambdas = []

    for lambda_name, data in _resources.items():
        code_uri = data["Properties"]["CodeUri"].replace("/", ".")
        if not code_uri.endswith("."):
            code_uri += "."
        handler = f"{code_uri}{data['Properties']['Handler']}"
        events = data["Properties"].get("Events")
        if not events:
            # mean it is authorizer or smth relative
            continue
        for _, event in events.items():
            method = event["Properties"]["Method"].lower()
            if method == "options":
                # this is for CORS, we not insteresting
                continue
            _lambda = {
                "name": lambda_name,
                "method": method,
                "endpoint": event["Properties"]["Path"],
                "handler": handler,
            }
            lambdas.append(_lambda)
    return lambdas, layers