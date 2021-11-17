from moncashify.constants import Constants
from moncashify.errors import (
    CredentialError,
    DebugError,
    AmountError,
    ZeroAmountError,
    NegativeAmountError,
    InvalidPhoneNumberError,
    DescriptionError,
    APIURLError,
)
# Python built-in packages
import datetime
    
class Core(object):
    def __init__(self, client_id, secret_key, debug=True):
        self._check_credentials_validation(client_id,secret_key,debug) # validate parameters values
        self.client_id = client_id
        self.secret_key = secret_key 
        self._debug = debug

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
        if int(amount) == 0:
            raise ZeroAmountError(amount)
        if amount < 0:
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
        if int(amount) == 0:
            raise ZeroAmountError(amount)
        if amount < 0:
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