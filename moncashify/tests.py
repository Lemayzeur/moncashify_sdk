import unittest
import moncashify
import random

# In Python 2.x: Be sure you uncomment the next three lines. Replace <your_path> with the repository absolute path
# import sys
# sys.path.append(<your_path>)
# import moncashify 

class TestAPI(unittest.TestCase):
    client_id = "f44336bc531e40d926edd8ff3eb59ca7"
    secret_key = "fqCEN-jbcK9K_zFjq74f5vY8bfG1i64cfFg4-LOnqPeS6PO6tDP2KmXwsYjBAt6C"
    order_id = 'SH02{}'.format(random.randrange(10,100))
    transaction_id = 'SSAHASUU323'
    amount = random.randrange(1,10) # HTG
    debug = True

    def test_token(self):
        moncash = moncashify.API(self.client_id, self.secret_key, self.debug)
        self.assertIsInstance(moncash.get_token(), dict)

    def test_payment(self):
        moncash = moncashify.API(self.client_id, self.secret_key, self.debug)
        message = 'Response is not a gateway'
        self.assertIsInstance(moncash.payment(self.order_id, self.amount), moncashify.HandleGateway)

    def test_redirect_url(self):
        moncash = moncashify.API(self.client_id, self.secret_key, debug=True)
        payment = moncash.payment(self.order_id, self.amount)
        url = payment.redirect_url
        self.assertEqual("https://" in url, True)

    # def test_transaction_details_by_order_id(self):
    #     moncash = moncashify.API(self.client_id, self.secret_key)
    #     self.assertIsInstance(moncash.transaction_details(order_id = "SH023"), dict)

    # def test_transaction_details_by_transaction_id(self):
    #     moncash = moncashify.API(self.client_id, self.secret_key)
    #     self.assertIsInstance(moncash.transaction_details(transaction_id = self.transaction_id), dict)