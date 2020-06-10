Requirements
===============

Compatible with Python 3.x or 2.x


Documentation
===============
	

Go to the `Official documentation <https://moncashify.readthedocs.io/en/latest>`_. 

Moncashify is distributed as a Python package through PyPI and it can be installed with tools like ``pip``:

.. code-block:: bash

   pip install moncashify


Getting Started
===============

If you’re new to Moncashify you can get started by following the tutorial `Implement Moncashify SDK In Your Python Projects <https://code9haiti.com/en/tutorials/implement-moncashify-sdk-in-your-python-projects>`_. 

Once the package is installed, it is easy to import the package into your project.

.. code-block:: python

   import moncashify



Use the ``API()`` method to initialize the process.

.. code-block:: python

   moncashify.API(client_id, secret_key, debug)


``client_id`` and ``secret_key`` can be found in your `Moncash administration <https://moncashbutton.digicelgroup.com/Moncash-business/>`_. The debugging setting (``debug``) will define whether you are in production or not. The default is ``True``, which means you are in development.

.. code-block:: python

   moncash = moncashify.API(client_id, secret_key, debug=True)
    
