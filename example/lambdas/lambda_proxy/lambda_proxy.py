from datetime import datetime


def lambda_handler(event, _):
    return {
        "statusCode": 200,
        "body": {"lambda2": "proxy", "requestDateTime2": str(datetime.now())},
    }
