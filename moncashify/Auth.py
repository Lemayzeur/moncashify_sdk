from moncashify import Constants
import json
import requests

def get_production_config():
    return {
        "config_type" : Constants.PRODUCTION_KEY,
        "redirect" : Constants.PRODUCTION_REDIRECT,
        "rest_api_endpoint" : Constants.REST_API_PRODUCTION_ENDPOINT,
    }

def get_development_config():
    return {
        "config_type" : Constants.DEVELOPMENT_KEY,
        "redirect" : Constants.DEVELOPMENT_REDIRECT,
        "rest_api_endpoint" : Constants.REST_API_DEVELOPMENT_ENDPOINT,
    }


def get_auth_info():
    rest_api_endpoint = get_production_config()["rest_api_endpoint"].split('//')
    client_id = None
    secret_key = None
    payload = {
        'scope':'read,write',
        'grant_type':'client_credentials',
    }
    try:
        url = rest_api_endpoint[0] + "//" + client_id + ":" + secret_key + "@" + \
                rest_api_endpoint[1] + Constants.AUTHENTIFICATION_URL
        print(url)
        response = requests.post(
            url = url,
            data = json.dumps(payload),
            headers = {
                'Accept':'application/json',
            },
        )
        if response.status_code == 200:
            return json.loads(response.text)
    except Exception as e:
        raise Exception(e)


def set_credentials(client_id, secret_key, development=True):
    return 0