.. _installation:

============
Installation
============

These instructions will get you a copy of ``shapepy`` up and running on your local machine. 
You will need a working copy of python on your machine, the valid versions are:

.. figure:: https://img.shields.io/pypi/pyversions/shapepy.svg?style=flat-square
   :width: 35%
   :alt: Available versions of python
   :align: center

How to install
------------------------------

Install the package and all of its dependencies can be done through the `python package index <https://pypi.org/project/shapepy/>`_:

.. code-block:: console

  $ pip install shapepy

You can also clone the git repository and install it

.. code-block:: console
  
  $ git clone https://github.com/compmec/shapepy
  $ cd shapepy
  $ pip install -e .


This package depends on the libraries:

* `numpy <https://numpy.org/>`_
* `rbool <https://pypi.org/project/rbool/>`_
* `matplotlib <https://matplotlib.org/>`_


Testing the Installation
------------------------

To verify if your installation works correctly, install ``pytest`` and run:

.. code-block:: console

  $ cd shapepy
  $ pytest .

