=================================
Fast SQLite -> numpy array loader
=================================

What is sqlite_numpy ?
----------------------

sqlite_numpy allows to load numpy arrays from a `SQLite <https://www.sqlite.org>` query and it does it as fast as pure C-code.

.. code-block:: python

    import pprint
    import sys
    import time

    import sqlite_numpy

    with sqlite_numpy.Database("test.sqlite") as db, db.execute("select * from my_table") as proxy:
        arrays = proxy.fetchall()
        pprint.pprint({name: array[0:10] for name, array in arrays.items()})


Features
--------

- Loads any numeric column of a SQLite query
- Created arrays can be double or int64 type
- Handles NULL as NaN values for float/double columns

Installing
----------

sqlite_numpy is best installed via pip:

.. code-block:: shell

    pip install sqlite_numpy

It only needs numpy as dependency and a valid sqlite3 library on the system.

Documentation
-------------

To be written.

Contributing
------------

sqlite_numpy is written using `Python <https://www.python.org>`_, C for interfacing with sqlite3 and  `Cython <https://www.cython.org>`_ for the glue between the C interface and Python.

- `Issue tracker <https://gitlab.com/sgrignard/sqlite_numpy/issues>`_
- `Source code <https://gitlab.com/sgrignard/sqlite_numpy>`_
