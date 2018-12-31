from collections import namedtuple
from datetime import datetime

import hashlib
import cx_Oracle
import os

from django.conf import settings
from django.core.cache import caches
from django.utils import timezone


class connect_db:

    conn = None

    def __enter__(self):

        # https://cx-oracle.readthedocs.io/en/latest/installation.html#quick-start-cx-oracle-installation
        # install cx_Oracle $python -m pip install cx_Oracle --upgrade
        # configure oracle client on PC https://oracle.github.io/odpi/doc/installation.html#linux

        os.environ["NLS_LANG"] = ".AL32UTF8"

        dsn_tns = cx_Oracle.makedsn(settings.DB_HOST, settings.DB_PORT, settings.DB_SERVER_NAME)
        self.connection = cx_Oracle.connect(settings.DB_USERNAME, settings.DB_PASSWORD, dsn_tns)

        def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
            if defaultType == cx_Oracle.BLOB:
                return cursor.var(cx_Oracle.LONG_BINARY, arraysize = cursor.arraysize)
        self.connection.outputtypehandler = OutputTypeHandler

        def execute_query(query, **kwargs):
            return self.execute_query(query, **kwargs)

        return execute_query

    def execute_query(self, query, **kwargs):
        # normalize the query
        query = ' '.join([s.strip() for s in query.strip().split('\n')])

        curs = self.connection.cursor()
        curs.execute(query, **kwargs)
        row_builder = namedtuple('Row', [f[0] for f in curs.description])

        def _fix_value(value):
            if isinstance(value, datetime):
                return timezone.make_aware(value, is_dst=False)
            else:
                return value

        for row in curs.fetchall():
            yield row_builder(*[_fix_value(v) for v in row])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


"""
def _execute_query(query, **kwargs):

    # normalize the query
    query = ' '.join([s.strip() for s in query.strip().split('\n')])

    # https://cx-oracle.readthedocs.io/en/latest/installation.html#quick-start-cx-oracle-installation
    # install cx_Oracle $python -m pip install cx_Oracle --upgrade
    # configure oracle client on PC https://oracle.github.io/odpi/doc/installation.html#linux


    os.environ["NLS_LANG"] = ".AL32UTF8"

    dsn_tns = cx_Oracle.makedsn(settings.DB_HOST, settings.DB_PORT, settings.DB_SERVER_NAME)
    connection = cx_Oracle.connect(settings.DB_USERNAME, settings.DB_PASSWORD, dsn_tns)

    def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
        if defaultType == cx_Oracle.BLOB:
            return cursor.var(cx_Oracle.LONG_BINARY, arraysize = cursor.arraysize)
    connection.outputtypehandler = OutputTypeHandler

    curs = connection.cursor()

    curs.execute(query, **kwargs)

    row_builder = namedtuple('Row', [f[0] for f in curs.description])

    def _fix_value(value):
        if isinstance(value, datetime):
            return timezone.make_aware(value)
        else:
            return value

    results = []
    for row in curs.fetchall():
        results.append(row_builder(*[_fix_value(v) for v in row]))

    connection.close()

    return results


def hashit(data):

    if type(data) == str:
        data = data.encode()

    if type(data) != bytes:
        raise Exception("Cannot hash %r" % data)

    return hashlib.md5(data).hexdigest()


def execute_query(query, cache_query=True, **kwargs):

    if cache_query:
        cache = caches['dump']

        key = hashit('%s\n%r' % (query, kwargs))
        values = cache.get(key)
        if not values:
            print('\n\nExecuting: %s\nkwargs:\n%r\n' % (query, kwargs))
            values = _execute_query(query, **kwargs)
            cache.set(key, values, 300)
    else:
        print('\n\nExecuting: %s\nkwargs:\n%r\n' % (query, kwargs))
        values = _execute_query(query, **kwargs)

    return values
"""
