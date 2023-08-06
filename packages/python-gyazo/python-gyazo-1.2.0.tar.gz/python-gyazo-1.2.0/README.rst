python-gyazo
============
.. image:: https://badge.fury.io/py/python-gyazo.svg
   :target: https://pypi.python.org/pypi/python-gyazo/
   :alt: PyPI version
.. image:: https://img.shields.io/pypi/pyversions/python-gyazo.svg
   :target: https://pypi.python.org/pypi/python-gyazo/
   :alt: PyPI Python versions
.. image:: https://travis-ci.org/ymyzk/python-gyazo.svg?branch=master
   :target: https://travis-ci.org/ymyzk/python-gyazo
   :alt: Build Status
.. image:: https://readthedocs.org/projects/python-gyazo/badge/?version=master
   :target: https://python-gyazo.readthedocs.io/
   :alt: Documentation Status
.. image:: https://codeclimate.com/github/ymyzk/python-gyazo/badges/gpa.svg
   :target: https://codeclimate.com/github/ymyzk/python-gyazo
   :alt: Code Climate
.. image:: https://coveralls.io/repos/ymyzk/python-gyazo/badge.svg?branch=master
   :target: https://coveralls.io/r/ymyzk/python-gyazo?branch=master
   :alt: Coverage Status

A Python wrapper for Gyazo API.

The full-documentation is available on `Read the Docs`_.

Requirements
------------
* Python 2.7+
* Python 3.4+

Installation
------------
.. code-block:: shell

   pip install python-gyazo

Note: Please use the latest version of setuptools & pip

.. code-block:: shell

   pip install -U setuptools pip


Usage
-----
At first, you must create an application and get an access token from https://gyazo.com/oauth/applications

.. code-block:: python

   from gyazo import Api


   client = Api(access_token='YOUR_ACCESS_TOKEN')

   ### Get a list of images
   images = client.get_image_list()
   for image in images:
       print(str(image))

   ### Using an image model
   image = images[0]
   print("Image ID: " + image.image_id)
   print("URL: " + image.url)

   ### Download an image
   if image.url:
       with open(image.filename, 'wb') as f:
           f.write(image.download())

   ### Upload an image
   with open('sample.png', 'rb') as f:
       image = client.upload_image(f)
       print(image.to_json())

   ### Delete an image
   client.delete_image('IMAGE_ID')

   ### oEmbed
   image = images[0]
   print(client.get_oembed(image.permalink_url))

Backup
------
``gyazo-backup`` is moved to `python-gyazo-backup`_.

License
-------
MIT License. Please see `LICENSE`_.

.. _Read the Docs: https://python-gyazo.readthedocs.io/
.. _python-gyazo-backup: https://github.com/ymyzk/python-gyazo-backup
.. _LICENSE: LICENSE
