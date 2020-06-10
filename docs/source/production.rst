In production
=============


To start using production credentials, initialize the API by overriding the third API parameter ``debug``.

.. code-block:: bash

   moncash = moncashify.API(client_id, secret_key, debug=False)


Using the instance
^^^^^^^^^^^^^^^^^^

change the value of the ``debug`` can be done with the instance. 

.. code-block:: bash

   moncash = moncashify.API(client_id, secret_key)
   moncash.debug = False


