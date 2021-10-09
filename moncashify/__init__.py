from moncashify.constants import Constants
from moncashify.exceptions import (
    CredentialError,
    DebugError,
    AmountError,
    ZeroAmountError,
    NegativeAmountError,
    InvalidPhoneNumberError,
    DescriptionError,
    QueryError,
    TokenError,
    OrderNotFound,
    TransactionNotFound,
)
import datetime
import json 
import base64

import requests
import sys

if sys.version_info >= (3, 0): # Python 3.X
    import urllib.parse as urllib
else: # Python 2.x
    import urllib

VERSION = '0.3.0'
__version__ = VERSION
version = VERSION

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
        if not isinstance(client_id,str):
            raise CredentialError(client_id)
        if not isinstance(secret_key,str):
            raise CredentialError(secret_key)
        if not isinstance(debug,bool):
            raise DebugError(debug)

    def _check_tranfer_values_validation(self, amount, receiver_number, description):
        receiver_number = str(receiver_number)
        if not isinstance(amount, int) and not isinstance(amount, float):
            raise AmountError(amount)
        if float(amount) == 0:
            raise ZeroAmountError(amount)
        if float(amount) < 0:
            raise NegativeAmountError(amount)
        if not receiver_number.isdigit() or \
            (len(receiver_number) != 8 and len(receiver_number) != 11) or \
            (len(receiver_number) == 11 and receiver_number[:3] != '509'):
            raise InvalidPhoneNumberError(receiver_number)
        if not isinstance(description,str) or len(description) > 255:
            raise DescriptionError(description)

    def _check_values_validation(self, order_id, amount):
        if not isinstance(amount, int) and not isinstance(amount, float):
            raise AmountError(amount)
        if float(amount) == 0:
            raise AmountZeroError(amount)
        if float(amount) < 0:
            raise NegativeAmountError(amount)

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
        ''' Check whether the token response does exist to avoid repeating calls within the 59 seconds'''
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
            raise CredentialError("Keys", "Credentials client_id or secret_key are not present")
        if self._token_response_exists():
            return self.token_response
        rest_api_endpoint = self._get_endpoint("rest_api")
        payload = {}
        params = {
            'scope':'read,write',
            'grant_type':'client_credentials',
        }
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
            response_dict = json.loads(response.text)
            raise TokenError(response_dict.get('status') or response.status_code, 
                response_dict.get('error', ''))

        self.token_date_query = datetime.datetime.now()
        return json.loads(response.text)

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
            response_dict = json.loads(response.text)
            raise QueryError(response_dict.get('status') or response.status_code, 
                response_dict.get('error', ''), 'Error while fetching payment data')
        
        response = json.loads(response.text)
        response['order_id'] = order_id
        response['amount'] = amount
        gateway = HandleGateway(self, response)
        return gateway

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
            response_dict = json.loads(response.text)
            if response.status_code == 404:
                raise OrderNotFound(kwargs.get('order_id')) if 'order_id' in kwargs else TransactionNotFound(kwargs.get('transaction_id'))
            raise QueryError(response_dict.get('status') or response.status_code, 
                response_dict.get('error', ''), 'Error while fetching transaction data')
            
        # convert response to python dictionnary
        payments_list = json.loads(response.text)
        return self._format_transaction_payment(payments_list)

    def transaction_details_by_order_id(self, order_id):
        return self.transaction_details(order_id=order_id)

    def transaction_details_by_transaction_id(self, transaction_id):
        return self.transaction_details(transaction_id=transaction_id)

    def transfer(self, amount, receiver_number, description=''):
        '''To transfer funds to another Moncash number'''
        self._check_tranfer_values_validation(amount, receiver_number, description) # validate values
        token_response = self.get_token() # get the token reponse as dict
        rest_api_endpoint = self._get_endpoint("rest_api") # get the endpoint
        payload = {'amount':amount, 'receiver':receiver_number, 'desc':description} # body request to be sent as json
        
        response = requests.post(
            url = rest_api_endpoint + Constants.TRANSFER_URL,
            data = json.dumps(payload),
            headers = {
                'Accept':'application/json',
                'Authorization':'Bearer ' + token_response['access_token'],  
                'content-type': 'application/json'
            },
        )
        if (not response or response.status_code < 200 or response.status_code > 400):
            response_dict = json.loads(response.text)
            raise QueryError(response_dict.get('status') or response.status_code, 
                response_dict.get('error', ''), 'Error while fetching transfer data')

        response = json.loads(response.text)
        return {
            'transfer_details':{
                'transaction_id':response['transaction_id'],
                'amount':response['amount'],
                'receiver_number':response['receiver'],
                'description':response['desc'],
            },
            'message':response['message'],
            'timestamp':response['timestamp'],
            "status": response['status'],
        }

    @property
    def state(self):
        return 'DEBUG %s' % self._debug

    @property
    def version(self):
        return VERSION 
    
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