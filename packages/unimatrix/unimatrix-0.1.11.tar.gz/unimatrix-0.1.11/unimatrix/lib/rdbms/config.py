import copy
import os

from unimatrix.const import SECDIR
from unimatrix.lib.datastructures import DTO


__all__ = ['parse_environment']


def _parse_bool(value):
    if value is None:
        return None
    return value == '1'


ENVIRONMENT_VARIABLES = [
    ('DB_HOST', 'host', False, str),
    ('DB_PORT', 'port', False, int),
    ('DB_NAME', 'name', False, str),
    ('DB_USERNAME', 'username', False, str),
    ('DB_PASSWORD', 'password', False, str),
    ('DB_CONNECTION_MAX_AGE', 'max_age', False, int),
    ('DB_AUTOCOMMIT', 'autocommit', False, _parse_bool)
]


#: Default values by engine.
DEFAULTS = {
    'postgresql': {
        'host': "localhost",
        'port': 5432,
    },
    'mysql': {
        'host': "localhost",
        'port': 3306,
    },
    'sqlite': {
        'name': ":memory:"
    }
}


def _get_computed_value(engine, name, opts):
    computed = None
    if name == 'host':
        computed = DEFAULT_HOSTS[engine]
    elif name == 'port':
        computed = DEFAULT_PORTS[engine]
    else:
        raise NotImplementedError
    return computed


def parse_environment(env):
    """Parses a database connection from the operating system
    environment based on the ``DB_*`` variables. Return a
    datastructure containing the configuration, or ``None`` if
    it was not defined.
    """
    # If no engine is specified, then the application does not
    # get its database connection configuration from environment
    # variables.
    engine = env.get('DB_ENGINE')
    if engine is None:
        return None

    if engine not in DEFAULTS:
        raise ValueError("Unsupported DB_ENGINE: %s" % engine)

    opts = DTO()
    for name, attname, required, cls in ENVIRONMENT_VARIABLES:
        default = DEFAULTS[engine].get(attname)
        value = env.get(name)
        if value is None:
            value = default
        opts[attname] = cls(value) if value is not None else value
        if required and not value and not default:
            raise NotImplementedError

    opts.engine = engine
    return opts


def load(env=None, config_dir=os.path.join(SECDIR, 'rdbms/connections')):
    """Loads the configured database connections from the operating
    system environment variables and the Unimatrix configuration files.

    Database connections are loaded with the following precedence:

    - Environment variables
    - Unimatrix Database Connection (UDC) files.

    Args:
        env (dict): a dictionary holding environment variables. Defaults
            to ``os.environ``.
        config_dir (str): a directory on the local filesystem holding
            the database connection configuration files. Defaults to
            `SECDIR/rdbms/connections`.

    Returns:
        dict
    """
    connections = {}
    self = parse_environment(copy.deepcopy(env or os.environ))
    if self:
        connections['self'] = self
    return connections
