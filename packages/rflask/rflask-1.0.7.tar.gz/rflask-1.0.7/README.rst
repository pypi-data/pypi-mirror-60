=======================
Init Flask Restful Api
=======================

------------
Installing
------------

Install and update using `pip`_:

.. code-block:: text

    pip install -U rflask

-------------------
A Simple Example
-------------------

.. code-block:: text

    $ rflask init
    project_name: [flask-restful-api-20200125-090404]
    author: [Deacon]
    author_email: [deacon@example.com]
    description: [Flask restful api project.]
    ...
    ...
    Create file /Users/donghp/Downloads/Git_doc/PythonProject/init-flask-restful-api/flask-restful-api-20200125-090404/supervisord_example.conf

    Done.

**Project dir tree**:

.. code-block:: text

    .
    ├── applications
    │   ├── test
    │   │   ├── README.rst
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── user
    │   │   ├── README.rst
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   └── views.py
    │   └── __init__.py
    ├── enums
    │   └── __init__.py
    ├── exceptions
    │   ├── __init__.py
    │   └── project_excepions.py
    ├── flask_ext
    │   ├── __init__.py
    │   └── logger.py
    ├── logs
    ├── requirements
    │   ├── dev.txt
    │   └── prod.txt
    ├── scripts
    │   └── __init__.py
    ├── utils
    │   ├── __init__.py
    │   └── commands.py
    ├── README.rst
    ├── __init__.py
    ├── app.py
    ├── autoapp.py
    ├── compat.py
    ├── database.py
    ├── extensions.py
    ├── gunicorn.conf
    ├── gunicorn_example.conf
    ├── settings.py
    ├── setup.py
    ├── supervisord.conf
    └── supervisord_example.conf

Then, you can do like this:

.. code-block:: text

    $ cd your_project
    $ pip install pipenv
    $ pipenv install --dev
    $ pipenv run python app.py

     * Serving Flask app "autoapp" (lazy loading)
     * Environment: dev
     * Debug mode: on
    2020-01-23 13:03:24,151 [4554636736:MainThread] [_internal.py:_internal:_log] [INFO]:  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    2020-01-23 13:03:24,152 [4554636736:MainThread] [_internal.py:_internal:_log] [INFO]:  * Restarting with stat
    2020-01-23 13:03:24,600 [4616764864:MainThread] [_internal.py:_internal:_log] [WARNING]:  * Debugger is active!
    2020-01-23 13:03:24,604 [4616764864:MainThread] [_internal.py:_internal:_log] [INFO]:  * Debugger PIN: 186-303-110

-------------------
Deploy to docker
-------------------

In your project root dir, open the terminal:

.. code-block:: text

    $ git clone ***.git
    $ cd <your_project>
    $ docker-compose up

------
Links
------

* Documentation: https://github.com/Deacone/init-flask-restful-api/blob/master/README.rst
* Code: https://github.com/Deacone/init-flask-restful-api
* Issue tracker: https://github.com/Deacone/init-flask-restful-api/issues

.. _pip: https://pip.pypa.io/en/stable/quickstart/



