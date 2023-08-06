RobotFramework HTTP RabbitMQ
============================

|Build Status|

Short Description
-----------------

`Robot Framework`_ library for for working with RabbitMQ via Management HTTP API.
Based on `robotframework-rabbitmq`_ 

Installation
------------

Install the library from PyPI using pip:

::

    pip install robotframework-http-rabbitmq

Documentation
-------------

See keyword documentation for RabbitMQ library on `GitHub`_.

Example
-------

.. code-block::

    *** Settings ***
    Library    RabbitMq
    Library    Collections

    *** Test Cases ***
    Simple Test
        Create Rabbitmq Connection    my_host_name    15672    5672    guest    guest    alias=rmq
        ${overview}=    Overview
        Log Dictionary    ${overview}
        Close All Rabbitmq Connections

License
-------

Apache License 2.0

.. _Robot Framework: http://www.robotframework.org
.. _GitHub: https://adsith-pv.github.io/robotframework-http-rabbitmq
.. _robotframework-rabbitmq: https://github.com/peterservice-rnd/robotframework-rabbitmq

.. |Build Status| image:: https://travis-ci.org/adsith-pv/robotframework-http-rabbitmq.svg?branch=master
    :target: https://travis-ci.org/adsith-pv/robotframework-http-rabbitmq
