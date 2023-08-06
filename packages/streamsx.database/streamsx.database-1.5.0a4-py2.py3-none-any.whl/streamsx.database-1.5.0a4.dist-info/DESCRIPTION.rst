Overview
========

Provides functions to run SQL statements to a database, for example IBM Db2 Warehouse.

This package exposes the `com.ibm.streamsx.jdbc <https://ibmstreams.github.io/streamsx.jdbc/>`_ toolkit as Python methods for use with Streaming Analytics service on
IBM Cloud and IBM Streams including IBM Cloud Pak for Data.

* `Streaming Analytics service <https://console.ng.bluemix.net/catalog/services/streaming-analytics>`_
* `IBM Streams developer community <https://developer.ibm.com/streamsdev/>`_
* `IBM Db2 Warehouse <https://www.ibm.com/cloud/db2-warehouse-on-cloud>`_


Sample
======

A simple example of a Streams application that creates a table, inserts a row and deletes the table::

    from streamsx.topology.topology import *
    from streamsx.topology.schema import CommonSchema, StreamSchema
    from streamsx.topology.context import submit
    import streamsx.database as db

    topo = Topology()
    sql_create = 'CREATE TABLE RUN_SAMPLE (A CHAR(10), B CHAR(10))'
    sql_insert = 'INSERT INTO RUN_SAMPLE (A, B) VALUES (\'hello\', \'world\')'
    sql_drop = 'DROP TABLE RUN_SAMPLE'
    s = topo.source([sql_create, sql_insert, sql_drop]).as_string()
    res_sql = db.run_statement(s, credentials)
    res_sql.print()
    submit('STREAMING_ANALYTICS_SERVICE', topo)
    # Use for IBM Streams including IBM Cloud Private for Data
    # submit ('DISTRIBUTED', topo)

Documentation
=============

* `streamsx.database package documentation <http://streamsxdatabase.readthedocs.io>`_


