import json
import logging
import os

import kinde_sdk.management

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def ping(event, context):

    body = {
        "message": "Pong!",
    }

    response = {
        "statusCode"    : 200, 
        "headers": {
            "Access-Control-Allow-Origin": "https://jamstack-auth.publicntp.net",
            "Content-Type": "application/json",
        },
        "body"          : json.dumps(body, indent=4, sort_keys=True), 
    }

    return response


def user_get(event, context):
    if 'requestContext' not in event or                                             \
            'authorizer' not in event['requestContext'] or                          \
            'jwt' not in event['requestContext']['authorizer'] or                   \
            'claims' not in event['requestContext']['authorizer']['jwt'] or         \
            'sub' not in event['requestContext']['authorizer']['jwt']['claims']:
        body = {
            "error": "event['requestContext']['authorizer']['jwt']['claims']['sub'] not passed to Lambda",
        }

        return {
            "statusCode"    : 500,
            "headers": {
                "Access-Control-Allow-Origin": "https://jamstack-auth.publicntp.net",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "body"          : json.dumps(body, indent=4, sort_keys=True) + "\n",
        }

    client_oauth_claim_sub: str = event['requestContext']['authorizer']['jwt']['claims']['sub']

    logger.info(f"Received authorized API call from sub = \"{client_oauth_claim_sub}\"")


    # Get info about our user, taken from sub field of JWT claims that APIGW put in the event context
    
    # Get a client to the management API
    mgmt_client = kinde_sdk.management.ManagementClient(
        domain="sixbuckssolutionsllc.kinde.com",
        client_id=os.environ.get("MGMT_API_CLIENT_ID"),
        client_secret=os.environ.get("MGMT_API_CLIENT_SECRET"),
    )

    user = mgmt_client.get_user(id=client_oauth_claim_sub)

    body = user.to_dict()


    logger.debug(f"Successfully queried user")
    logger.debug(json.dumps(body, indent=4, sort_keys=True))

    response = {
        "statusCode"    : 200,
        "headers": {
            "Access-Control-Allow-Origin": "https://jamstack-auth.publicntp.net",
            "Access-Control-Allow-Credentials": True,
            "Content-Type": "application/json",
        },
        "body"          : json.dumps(body, indent=4, sort_keys=True, default=str) + "\n",
    }

    return response

