import hashlib
import cx_Oracle
import os

from django.conf import settings
from django.core.cache import caches


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

    columns = {}

    def type2str(type):
        if type == cx_Oracle.NUMBER:
            return 'number'
        if type == cx_Oracle.STRING:
            return 'string'
        if type == cx_Oracle.FIXED_CHAR:
            return 'fixed_char'
        if type == cx_Oracle.DATETIME:
            return 'datetime'
        if type == cx_Oracle.LONG_STRING:
            return 'long_string'
        if type == cx_Oracle.BINARY:
            return 'binary'
        if type == cx_Oracle.BLOB:
            return 'blob'
        if type == cx_Oracle.ROWID:
            return 'rowid'

        return repr(type)


    def get_columns(cursor):
        columns = []
        for field in cursor.description:
            name, type, display_size, internal_size, precision, scale, null_ok = field
            columns.append({
                    'name': name,
                    'type': type2str(type),
                    'display_size': display_size,
                    'internal_size': internal_size,
                    'precision': precision,
                    'scale': scale,
                    'null_ok': null_ok,
                })
        return columns

    curs.execute(query, **kwargs)

    columns = get_columns(curs)

    rows = curs.fetchall()

    connection.close()

    return columns, rows


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
    columns, rows = values
    return columns, rows
