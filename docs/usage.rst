=====
Usage
=====

Importing
#########

To use itstools in a project just import the package:

.. code-block:: python

    import itstools

You can check the last version of the package via::

    itstools.__version__

The structure of the package is as follows::

    itstools
    ├── __init__.py
    ├── connectv2x
    ├── macrotrasim
    └── vplatoon

To import a special function from the package :: 

    from itstools.connectv2x import Vehicle