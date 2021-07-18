from layers.some.some_module import custom_function_from_layer


def lambda_handler(event, context):
    return {"lambda_result": custom_function_from_layer()}
