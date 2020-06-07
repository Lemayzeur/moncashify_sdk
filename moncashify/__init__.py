from moncashify.constants import Constants
import datetime
import json 
import base64

import requests
import sys

if sys.version_info >= (3, 0): # Python 3.X
    import urllib.parse as urllib
else: # Python 2.x
    import urllib

class API:
    def __init__(self, client_id, secret_key, debug=True):
        self._check_credentials_validation(client_id,secret_key,debug) # validate parameters values
        self.client_id = client_id
        self.secret_key = secret_key 
        self._debug = debug

        self.token_response = {}
        self.token_date_query = None 

    def __repr__(self):
        return 'Moncashify Object - Client ID: %s' % self.client_id

    def _check_credentials_validation(self, client_id, secret_key, debug):
        error_message = ''
        if not isinstance(client_id,str):
            error_message += " <client_id> should be a string. "
        if not isinstance(secret_key,str):
            error_message += " <secret_key> should be a string. "
        if not isinstance(debug,bool):
            error_message += " <debug> should be boolean. "
        if error_message:
            raise ValueError(error_message.strip())

    def _check_values_validation(self, order_id, amount):
        error_message = ''
        if not isinstance(amount, int) and not isinstance(amount, float):
            error_message += " <amount> should be a integer or float. "
        if error_message:
            raise ValueError(error_message.strip())

    def _development_config(self):
        ''' This config when debug is True [Sandbox mode]'''
        return {
            "config_type" : Constants.DEVELOPMENT_KEY,
            "redirect" : Constants.DEVELOPMENT_REDIRECT,
            "rest_api" : Constants.REST_API_DEVELOPMENT_ENDPOINT,
        }
    
    def _format_transaction_payment(self, payments_list):
        return {
            "path":payments_list["path"],
            "payment":{
                'reference':payments_list['payment']['reference'],
                'transactionId':payments_list['payment']['transaction_id'],
                'cost':payments_list['payment']['cost'],
                'message':payments_list['payment']['message'],
                'payer':payments_list['payment']['payer'],
            },
            "timestamp":payments_list["timestamp"],
            "status" : payments_list["status"],
        }

    def _get_endpoint(self, key):
        ''' get the appropriate token endpoint according to debug state'''
        return self._development_config()[key] if self._debug else self._production_config()[key]

    def _production_config(self):
        ''' This config when debug is False [Live mode]'''
        return {
            "config_type" : Constants.PRODUCTION_KEY,
            "redirect" : Constants.PRODUCTION_REDIRECT,
            "rest_api" : Constants.REST_API_PRODUCTION_ENDPOINT,
        }

    def _token_response_exists(self):
        ''' Check whether the token reponse does exist to avoid repeating calls within the 59 seconds'''
        if isinstance(self.token_date_query, datetime.datetime) \
            and isinstance(self.token_response, dict) \
            and 'access_token' in self.token_response:
            time_elapsed = datetime.datetime.now() - self.token_date_query
            if time_elapsed.total_seconds() < 59:
                return True
        return False

    def get_token(self):
        '''Authenticate to call the resources of the Rest API MonCash'''
        if not self.client_id or not self.secret_key:
            raise ValueError("Credentials client_id or secret_key are not present")
        if self._token_response_exists():
            return self.token_response
        rest_api_endpoint = self._get_endpoint("rest_api")
        payload = {}
        params = {
            'scope':'read,write',
            'grant_type':'client_credentials',
        }
        try:
            url = rest_api_endpoint + Constants.AUTHENTIFICATION_URL + "?" + urllib.urlencode(params)
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
        ''' Override credentials[client_id,secret_key] of an instance'''
        self._check_credentials_validation(client_id,secret_key,self._debug)
        self.client_id = client_id
        self.secret_key = secret_key

    def payment(self, order_id, amount):
        '''To make a payment with the <order_id> and the <amount>'''
        self._check_values_validation(order_id, amount) # validate values
        token_response = self.get_token() # get the token reponse as dict
        rest_api_endpoint = self._get_endpoint("rest_api") # get the endpoint
        payload = { 'orderId':order_id, 'amount':amount } # body request to be sent as json
        try:
            response = requests.post(
                url = rest_api_endpoint + Constants.CREATE_PAYMENT_URL,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Bearer ' + token_response['access_token'],  
                    'content-type': 'application/json'
                },
            )
            if (not response or response.status_code < 200 or response.status_code > 400):
                print('%s: Error while fetching data' % response.status_code)
            else:
                response = json.loads(response.text)
                response['order_id'] = order_id
                response['amount'] = amount
                gateway = HandleGateway(self, response)
                return gateway
        except Exception as error:
            print('Caught this error: ' + repr(error))

    def transaction_details(self, **kwargs):
        ''' Get a payment details with a <transaction_id> or <order_id>'''
        token_response = self.get_token() # get the token reponse as dict
        rest_api_endpoint = self._get_endpoint("rest_api") # get the endpoint
         
        if 'order_id' in kwargs:
            url = rest_api_endpoint + Constants.RETRIEVE_ORDER_URL
            payload = {'orderId':kwargs.get('order_id')} # set the <order_id>
        elif 'transaction_id' in kwargs:
            url = rest_api_endpoint + Constants.RETRIEVE_TRANSACTION_PAYMENT_URL
            payload = {'transactionId':kwargs.get('transaction_id')} # set the <transaction_id>
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
            else:
                payments_list = json.loads(response.text) # convert response to json or dict
                return self._format_transaction_payment(payments_list)
        except Exception as error:
            print('Caught this error: ' + repr(error))

    def transaction_details_by_order_id(self, order_id):
        return self.transaction_details(order_id=order_id)

    def transaction_details_by_transaction_id(self, transaction_id):
        return self.transaction_details(transaction_id=transaction_id)

    @property
    def state(self):
        return 'DEBUG %s' % self._debug
    
class HandleGateway:
    def __init__(self, instance, response):
        self.instance = instance
        self.gateway_response = {
            "debug" : response["mode"] == 'sandbox',
            "order_id" : response["order_id"],
            "amount" : response["amount"],
            "mode" : response["mode"],
            "token_details" : {
                'token':response['payment_token']['token'],
                "created" : datetime.datetime.strptime(
                    response['payment_token']["created"],"%Y-%m-%d %H:%M:%S:%f"
                ),
                "expired" : datetime.datetime.strptime(
                    response['payment_token']["expired"],"%Y-%m-%d %H:%M:%S:%f"
                ),
            },
            "timestamp" : response["timestamp"],
            "status" : response["status"],
        }
    
    def __repr__(self):
        return "Payment object - Order ID: %s, Amount: %s" % (self.gateway_response['order_id'],
                        self.gateway_response['amount'])

    def get_redirect_url(self):
        return self.redirect_url

    def get_response(self):
        self.gateway_response['url'] = self.redirect_url
        return self.gateway_response

    @property
    def redirect_url(self):
        return self.instance._get_endpoint("redirect") + \
                Constants.PAYMENT_GATEWAY_URL + "?token=" + \
                    self.gateway_response['token_details']['token']