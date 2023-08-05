import copy
import os

from unimatrix.lib import rdbms


ENGINE_MAPPING = {
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'mysql': 'django.db.backends.mysql',
    'sqlite': 'django.db.backends.sqlite3'
}


def _load(env=None):
    databases = {}
    connections = rdbms.load_config(
        env=copy.deepcopy(env or os.environ))
    if not connections:
        return {}

    # The 'self' connection is the default connection in
    # Django.
    if 'self' in connections:
        connections['default'] = connections.pop('self')

    # Construct the Django database connections from the parsed
    # configuration.
    for alias in dict.keys(connections):
        connection = connections[alias]
        databases[alias] = {
            'HOST': connection.host,
            'PORT': connection.port,
            'NAME': connection.name,
            'USER': connection.username,
            'PASSWORD': connection.password,
            'PORT': connection.port,
            'ENGINE': ENGINE_MAPPING[connection.engine],
            'CONN_MAX_AGE': connection.max_age,
            'AUTOCOMMIT': connection.autocommit
        }

        # Remove empty keys.
        for k in list(dict.keys(databases[alias])):
            if databases[alias].get(k) is not None:
                continue
            del databases[alias][k]

    return databases


DATABASES = _load()
