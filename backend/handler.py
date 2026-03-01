import json
import logging
import os

import boto3                    # Needed to read secrets from Systems Manager Parameter Store
import kinde_sdk.management

_logger = logging.getLogger()
_logger.setLevel(logging.INFO)

_allowed_origin_url: str = "https://serverless-jamstack-auth.click"

_ssm_client = boto3.client('ssm')

_kinde_secrets_param_store_paths: list[str] = [
    "/serverless-jamstack-auth/backend/auth/domain",
    "/serverless-jamstack-auth/backend/auth/client-id",
    "/serverless-jamstack-auth/backend/auth/client-secret",
]


def ping(event, context):

    body = {
        "message": "Pong!",
    }

    response = {
        "statusCode"    : 200, 
        "headers": {
            "Access-Control-Allow-Origin": _allowed_origin_url,
            "Content-Type": "application/json",
        },
        "body"          : json.dumps(body),
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
                "Access-Control-Allow-Origin": _allowed_origin_url,
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "body"          : json.dumps(body),
        }

    client_oauth_claim_sub: str = event['requestContext']['authorizer']['jwt']['claims']['sub']

    _logger.info(f"Received authorized API call from sub = \"{client_oauth_claim_sub}\"")

    # Retrieve our OAuth client ID and client secret needed to access the Kinde Management API FROM
    #   this confidential client ("confidential client" means the client secret is *never* expposed to
    #   the untrusted JavaScript client)
    kinde_mgmt_api_secrets: dict[str, str] = _get_kinde_secrets()

    # Get a client to the management API
    mgmt_client = kinde_sdk.management.ManagementClient(
        domain=kinde_mgmt_api_secrets['domain'],
        client_id=kinde_mgmt_api_secrets['client_id'],
        client_secret=kinde_mgmt_api_secrets['client_secret']
    )

    user = mgmt_client.get_user(id=client_oauth_claim_sub)

    body = user.to_dict()


    _logger.debug(f"Successfully queried user")
    _logger.debug(json.dumps(body, indent=4, sort_keys=True))

    response = {
        "statusCode"    : 200,
        "headers": {
            "Access-Control-Allow-Origin": _allowed_origin_url,
            "Access-Control-Allow-Credentials": True,
            "Content-Type": "application/json",
        },
        "body"          : json.dumps(body), 
    }

    return response


def _get_kinde_secrets() -> dict[str, str]:

    # Read two secrets we need to talk to Kinde Mgmt API
    parameter_store_response = _ssm_client.get_parameters( Names=client_token_signing_jwks_param_store_paths )

    if not 'Parameters' in parameter_store_response 
        raise RuntimeError("Parameter store response did not have Parameters field")

    retrieved_values: dict[str, str] = {}

    ssm_path_to_key_mapping: dict[str, str] = {
        "/backend/auth/domain"          : "domain",
        "/backend/auth/client-id"       : "client_id",
        "/backend/auth/client-secret"   : "client_secret",
    }

    for curr_param_entry in parameter_store_response['Parameters']:
        for possible_path_ending in ssm_path_to_key_mapping:
            if curr_param_entry['Name'].endswith(possible_path_ending)
                retrieved_values[ ssm_path_to_key_mapping[possible_path_ending] ] = curr_param_entry['Value']
                # Done processing this parameter
                break
        else:
            raise RuntimeError(f"Did not find mapping for parameter with Name \"{curr_param_entry['Name']}\"")

    # Sanity check result has all required values
    for required_key in ssm_path_to_key_mappings.values():
        if required_key not in retrieved_values:
            raise RuntimeError(f"Did not populate required key \"{required_key\"")

    _logger.debug("Successfully read all required secrets from Parameter Store")

    return retrieved_values

