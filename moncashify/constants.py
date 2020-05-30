class Constants:
    VERSION = '1.0.0'

    AUTHENTIFICATION_URL = "/oauth/token"
    # REST_API_PRODUCTION_ENDPOINT = 'https://moncashbutton.digicelgroup.com/Api'
    REST_API_PRODUCTION_ENDPOINT = 'https://api.moncashbutton.digicelgroup.com'
    REST_API_DEVELOPMENT_ENDPOINT = 'https://sandbox.moncashbutton.digicelgroup.com/Api'  
    DEVELOPMENT_REDIRECT = "https://sandbox.moncashbutton.digicelgroup.com/Moncash-middleware"
    PRODUCTION_REDIRECT = "https://moncashbutton.digicelgroup.com/Moncash-middleware"

    PRODUCTION_KEY = 'live'
    DEVELOPMENT_KEY = 'sandbox'

    CREATE_PAYMENT_URL = "/v1/CreatePayment"  
    PAYMENT_GATEWAY_URL = '/Payment/Redirect'
    RETRIEVE_TRANSACTION_PAYMENT_URL = "/v1/RetrieveTransactionPayment" 
    RETRIEVE_ORDER_URL = "/v1/RetrieveOrderPayment" 