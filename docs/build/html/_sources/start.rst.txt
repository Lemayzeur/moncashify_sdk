Getting Started
===============

If you’re new to Moncashify you can get started by following the tutorial here. 

Once the package is installed, it is simple to import the package in your project.

.. code-block:: python

   import moncashify



Use the ``API()`` method to initialize the process.

.. code-block:: python

   moncashify.API(client_id, secret_key, debug)


``client_id`` and ``secret_key`` can be found in your Moncash Administration. The ``debug`` parameter will define whether you are in production or not. The default value is ``True``, which means that you are in development.

.. code-block:: python

   moncash = moncashify.API(client_id, secret_key, debug=True)


Make a payment
^^^^^^^^^^^^^^

Once you have to allow your customers to pay you, you need to have a unique ID for the order and the amount of money to charge your customers.

.. code-block:: python

   moncash = moncashify.API(client_id, secret_key)
   payment = moncash.payment(unique_order_id, amount_of_money)


The unique id is up to you, make sure that you never send duplicated identifications to the API, to avoid having doublons. 
The returned value is an object with the following attribute: ``redirect_url``. This attribute is the generated url that your customer will use to pay the order.

``instance.get_response()`` to have all the details related to the transaction request whether it’s successful or not.

``instance.get_redirect_url()`` to have the payment url.


Retrieve transaction details
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To retrieve details about a successful transaction, this process can be done with the ``order_id`` provided by you or the ``transaction_id`` generated  by the API itself.


.. code-block:: python

   moncash = moncashify.API(client_id, secret_key)
   moncash.transaction_details(order_id_or_transaction_id=order_id_or_transaction_id)


If you use transaction_details, you will need to provide the parameter ``order_id`` or ``transaction_id``

Using ``order_id``
##################

To get the transaction details with the ``order_id``, call the method ``transaction_details_by_order_id()`` with the ``order_id`` as parameter.

Using ``transaction_id``
########################

To get the transaction details with the ``transaction_id``, call the method ``transaction_details_by_transaction_id()`` with the ``transaction_id`` as parameter.


Change credentials
^^^^^^^^^^^^^^^^^^


It is not necessary to re-instantiate a moncashify object to set new client_id or cleint_secret. The method set_credentials(client_id, secret_key) will replace old credentials by the new one provided as parameters. 

.. code-block:: bash
   :linenos:

   moncash = moncashify.API(‘A12’,’POAK32’)
   print(moncash)

   moncash.set_credentials(‘0012’,’HAITI3923’)
   print(moncash)