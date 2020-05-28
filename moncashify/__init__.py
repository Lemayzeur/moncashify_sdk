import requests
import datetime
import json 
import base64
import urllib

VERSION = '1.0.0'

AUTHENTIFICATION_URL = "/oauth/token"
REST_API_PRODUCTION_ENDPOINT = 'https://moncashbutton.digicelgroup.com/Api'
# REST_API_PRODUCTION_ENDPOINT = 'https://api.moncashbutton.digicelgroup.com'
REST_API_DEVELOPMENT_ENDPOINT = 'https://sandbox.moncashbutton.digicelgroup.com/Api'  
DEVELOPMENT_REDIRECT = "https://sandbox.moncashbutton.digicelgroup.com/Moncash-middleware"
PRODUCTION_REDIRECT = "https://moncashbutton.digicelgroup.com/Moncash-middleware"

PRODUCTION_KEY = 'live'
DEVELOPMENT_KEY = 'sandbox'

CREATE_PAYMENT_URL = "/v1/CreatePayment"  
RETRIEVE_TRANSACTION_PAYMENT_URL = "/v1/RetrieveTransactionPayment" 
RETRIEVE_ORDER_URL = "/v1/RetrieveOrderPayment"  


class auth:
    def __init__(self, client_id, secret_key, debug=True):
        self.client_id = client_id
        self.secret_key = secret_key 
        self._debug = debug

        self.token_response = {}
        self.token_date_query = None 

    def __repr__(self):
        return 'Moncashify Object - Client ID: %s' % self.client_id

    def _development_config(self):
        return {
            "config_type" : DEVELOPMENT_KEY,
            "redirect" : DEVELOPMENT_REDIRECT,
            "rest_api_endpoint" : REST_API_DEVELOPMENT_ENDPOINT,
        }
    
    def _get_rest_api_endpoint(self):
        return self._development_config()["rest_api_endpoint"] if self._debug else self._production_config()["rest_api_endpoint"]

    def _get_transaction_payment(self, payments_list):
        return {
            "path":payments_list["path"],
            "payment":{
                'reference':payments_list['reference'],
                'transactionId':payments_list['transaction_id'],
                'cost':payments_list['cost'],
                'message':payments_list['message'],
                'payer':payments_list['payer'],
            },
            "timestamp":payments_list["timestamp"],
            "status" : payments_list["status"],
        }

    def _production_config(self):
        return {
            "config_type" : PRODUCTION_KEY,
            "redirect" : PRODUCTION_REDIRECT,
            "rest_api_endpoint" : REST_API_PRODUCTION_ENDPOINT,
        }

    def _token_response_exists(self):
        if isinstance(self.token_date_query, datetime.datetime) \
            and isinstance(self.token_response, dict) \
            and 'access_token' in self.token_response:
            time_elapsed = datetime.datetime.now() - self.token_date_query
            if time_elapsed.total_seconds() < 59:
                return True
        return False

    def get_token(self):
        if not self.client_id or not self.secret_key:
            raise ValueError("Credentials client_id or secret_key are not present")
        if self._token_response_exists():
            return self.token_response
        rest_api_endpoint = self._get_rest_api_endpoint()#.split('//')
        payload = {}
        params = {
            'scope':'read,write',
            'grant_type':'client_credentials',
        }
        try:
            url = rest_api_endpoint + AUTHENTIFICATION_URL + "?" + urllib.parse.urlencode(params)
            # url = rest_api_endpoint[0] + "//" + self.client_id + ":" + self.secret_key + "@" + \
                    # rest_api_endpoint[1] + AUTHENTIFICATION_URL
            auth_string = "%s:%s" % (self.client_id, self.secret_key)
            response = requests.post(
                url = url,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Basic ' + base64.encodestring(
                            auth_string.encode('ascii')
                        ).decode('ascii').replace('\n',''),  
                },
            )
            if (not response or response.status_code < 200 or response.status_code > 400):
                print('%s: Error while fetching data' % response.status_code)
            
            self.token_date_query = datetime.datetime.now()
            return json.loads(response.text)
        except Exception as error:
            print('Caught this error: ' + repr(error))

    def set_credentials(self, client_id, secret_key):
        self.client_id = client_id
        self.secret_key = secret_key

    def payment(self, order_id, amount):
        token_response = self.get_token()
        rest_api_endpoint = self._get_rest_api_endpoint()
        payload = { 'orderId':order_id, 'amount':amount }
        try:
            response = requests.post(
                url = rest_api_endpoint + CREATE_PAYMENT_URL,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Bearer ' + token_response['access_token'],  
                    'content-type': 'application/json'
                },
            )
            if (not response or response.status_code < 200 or response.status_code > 400):
                print('%s: Error while fetching data' % response.status_code)
            return json.loads(response.text)
        except Exception as error:
            print('Caught this error: ' + repr(error))
        return {}

    def transaction_details(self, **kwargs):
        token_response = self.get_token()
        rest_api_endpoint = self._get_rest_api_endpoint()
         
        if 'order_id' in kwargs:
            url = rest_api_endpoint + RETRIEVE_ORDER_URL
            payload = {'orderId':kwargs.get('order_id')}
        elif 'transaction_id' in kwargs:
            url = rest_api_endpoint + RETRIEVE_TRANSACTION_PAYMENT_URL
            payload = {'transactionId':kwargs.get('transaction_id')}
        else:
            raise NameError("<order_id> or <transction_id> is not defined")

        try:
            response = requests.post(
                url = url,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Bearer ' + token_response['access_token'],  
                    'content-type': 'application/json'
                },
            )
            if (not response or response.status_code < 200 or response.status_code > 400):
                print('%s: Error while fetching data' % response.status_code)
            return self._get_transaction_payment(json.loads(response.text))
        except Exception as error:
            print('Caught this error: ' + repr(error))
        return {}

    @property
    def state(self):
        return 'DEBUG %s' % self._debug
    