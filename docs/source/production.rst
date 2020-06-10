In production
=============


To start using production credentials, initial the API by overriding the third parameter of the API. It is imperative to pass the False, since the default value of debug is True.

.. code-block:: bash

   moncash = moncashify.API(client_id, secret_key, debug=False)


Using the instance
^^^^^^^^^^^^^^^^^^

change the value of the debug can be done with an instance. 

.. code-block:: bash

   moncash = moncashify.API(client_id, secret_key)
   moncash.debug = False


