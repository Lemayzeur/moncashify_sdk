## Synopsis

The official MonCash Python SDK.

## Requirements

Python >= 3.6<br/>
requests >= 2.22.0<br/>
json<br/>

## Documentation

    import moncashify
    
    # set credentials with debug True for development. False for production
    moncash = moncashify.auth(client_id='<client_id>', secret_key='<secret_key>', debug=True)
    
    # get the token
    moncash.info()
    
    moncash.payment(order_id, amount)
    
    moncash.transaction_details(order_id_or_transaction_id)
    
