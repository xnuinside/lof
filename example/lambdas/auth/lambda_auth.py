from datetime import datetime


def lambda_handler(event, _):
    return {
        "context": {
            "statusCode": 200,
            "body": {"lambda": "authorizer", "requestDateTime": str(datetime.now())},
        }
    }
