from datetime import datetime


def lambda_handler(_, context):
    return {
        "statusCode": 200,
        "body": {
            "lambda2": "proxy",
            "requestDateTime2": str(datetime.now()),
            "context": context,
        },
    }
