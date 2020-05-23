

def depot(phone, amount, create_client=True, description=None):
    balance = 0.3
    if(isinstance(amount,float) or isinstance(amount,int)):
        balance += amount
    else:
        raise ValueError("<amount> should be integer or float")
    