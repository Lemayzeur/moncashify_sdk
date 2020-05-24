from moncashify import Auth, Constants
import requests
import json 

def make_payment(order_id, amount, development=True):
    rest_api_endpoint = Auth.get_production_config()["rest_api_endpoint"]
    auth_info = Auth.get_auth_info()
    payload = {'orderId':order_id, 'amount':amount}

    try:
        response = requests.post(
            url = rest_api_endpoint + Constants.CREATE_PAYMENT_URL,
            data = json.dumps(payload),
            headers = {
                'Accept':'application/json',
                'Authorization':'Bearer ' + auth_info['access_token'],  
                'content-type': 'application/json'
            },
        )
        if response.status_code == 200:
            return json.loads(response.text)
    except Exception as e:
        raise Exception(e)

def get_details(**kwargs):
    rest_api_endpoint = Auth.get_production_config()["rest_api_endpoint"]
    auth_info = Auth.get_auth_info()
    
    if 'order_id' in kwargs:
        url = rest_api_endpoint + Constants.RETRIEVE_ORDER_URL
        payload = {'orderId':kwargs.get('order_id')}
    elif 'transaction_id' in kwargs:
        url = rest_api_endpoint + Constants.RETRIEVE_TRANSACTION_PAYMENT_URL
        payload = {'transactionId':kwargs.get('transaction_id')}
    else:
        raise NameError("<order_id> or <transction_id> is not defined")

    try:
        response = requests.post(
            url = url,
            data = json.dumps(payload),
            headers = {
                'Accept':'application/json',
                'Authorization':'Bearer ' + auth_info['access_token'],  
                'content-type': 'application/json'
            },
        )
        if response.status_code == 200:
            print(response.text)
            return get_transaction_payment(
                json.loads(response.text))
    except Exception as e:
        raise Exception(e)


def get_transaction_payment(payments_list):
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

       

