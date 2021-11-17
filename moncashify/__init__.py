from moncashify.constants import Constants
from moncashify.errors import (
    CredentialError,
    QueryError,
    TokenError,
    OrderNotFoundError,
    TransactionNotFoundError,
)
from moncashify.core import Core
from moncashify import service

# Python built-in packages
import datetime
import json

VERSION = '1.1.0'
__version__ = version = __VERSION__ = VERSION

class API(Core):
    def __init__(self, client_id, secret_key, debug=True):
        self.token_response = {}
        self.token_date_query = None 
        super(API, self).__init__(client_id, secret_key, debug)

    def __repr__(self):
        return 'Moncashify Object - Client ID: %s' % self.client_id

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
        url = rest_api_endpoint + Constants.AUTHENTIFICATION_URL + "?" + service.encode_url(params)
        auth_string = "%s:%s" % (self.client_id, self.secret_key)
        try:
            response, status_code = service.post(
                url = url,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Basic ' + service.encode_bytes(
                            auth_string.encode('ascii')
                        ).decode('ascii').replace('\n',''),  
                },
            )
        except Exception as e:
            raise TokenError('101', str(e))

        if (not response or status_code < 200 or status_code >= 400):
            response_dict = json.loads(response)
            raise TokenError(response_dict.get('status') or status_code, 
                response_dict.get('error', ''))

        self.token_date_query = datetime.datetime.now()
        return json.loads(response)

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
            response, status_code = service.post(
                url = rest_api_endpoint + Constants.CREATE_PAYMENT_URL,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Bearer ' + token_response['access_token'],  
                    'content-type': 'application/json'
                },
            )
        except Exception as e:
            raise TokenError('101', str(e))

        if (not response or status_code < 200 or status_code >= 400):
            response_dict = json.loads(response)
            raise QueryError(response_dict.get('status') or status_code, 
                response_dict.get('error', ''), 'Error while fetching payment data')
        
        response = json.loads(response)
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

        try:
            response, status_code = service.post(
                url = url,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Bearer ' + token_response['access_token'],  
                    'content-type': 'application/json'
                },
            )
        except Exception as e:
            raise TokenError('101', str(e))

        if (not response or status_code < 200 or status_code >= 400):
            response_dict = json.loads(response)
            if status_code == 404:
                raise OrderNotFoundError(kwargs.get('order_id')) if 'order_id' in kwargs else TransactionNotFoundError(kwargs.get('transaction_id'))
            raise QueryError(response_dict.get('status') or status_code, 
                response_dict.get('error', ''), 'Error while fetching transaction data')
            
        # convert response to python dictionnary
        payments_list = json.loads(response)
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

        try:
            response, status_code = service.post(
                url = rest_api_endpoint + Constants.TRANSFER_URL,
                data = json.dumps(payload),
                headers = {
                    'Accept':'application/json',
                    'Authorization':'Bearer ' + token_response['access_token'],  
                    'content-type': 'application/json'
                },
            )
        except Exception as e:
            raise TokenError('101', str(e))

        if (not response or status_code < 200 or status_code >= 400):
            response_dict = json.loads(response)
            raise QueryError(response_dict.get('status') or status_code, 
                response_dict.get('error', ''), 'Error while fetching transfer data')

        response = json.loads(response)
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
    
class HandleGateway(object):
    def __init__(self, instance, response):
        self.instance = instance

        try:
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
        except KeyError:
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = 'Error in line {0}. MonCash API endpoint responses updated'.format(exc_tb.tb_lineno)
            service.bug_report("URGENT", 'msg', level=3)
    
    def __repr__(self):
        return "Payment object - Order ID: %s, Amount: %s" % (self.gateway_response['order_id'],
                        self.gateway_response['amount'])

    def get_redirect_url(self): # URL that customers will you use to pay in their browser.
        return self.redirect_url

    def get_response(self):
         return self.response

    @property
    def redirect_url(self): # URL that customers will you use to pay in their browser.
        return self.instance._get_endpoint("redirect") + \
                Constants.PAYMENT_GATEWAY_URL + "?token=" + \
                    self.gateway_response['token_details']['token']

    @property
    def response(self):
        self.gateway_response['url'] = self.redirect_url
        return self.gateway_response