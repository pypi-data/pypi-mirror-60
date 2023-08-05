from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)


from traceback import format_exc

from trend_app_protect.logger import log
from trend_app_protect.plugins.dbapi2_helper import (
    ConnectionWrapper,
    wrap_connect,
)

# Name plugin so it can be enabled and disabled.
NAME = "sqli_psycopg2"
HOOKS_CALLED = ["sql_execute"]


def add_hooks(run_hook, get_agent_func=None, timer=None):
    """
    Add hooks to psycopg2.
    """
    try:
        import psycopg2
    except ImportError:
        return None

    meta = {
        "version": psycopg2.__version__,
        "apilevel": psycopg2.apilevel,
        "threadsafety": psycopg2.threadsafety,
        "paramstyle": psycopg2.paramstyle,
    }

    def mogrify(_connection, cursor, sql, params):
        # psycopg2 supports db calls only on the cursor
        try:
            return cursor.mogrify(sql, params)
        except Exception:
            log.debug("psycopg2.mogrify unable to mogrify: %s", format_exc())
            return sql

    # Wrap original connect function.
    wrapped_connect = wrap_connect(run_hook, get_agent_func, psycopg2.connect,
                                   "postgres", mogrify)

    # replace all references to connect
    psycopg2.connect = wrapped_connect

    # Psycopg2 has additional extensions. Some extensions take a connection as
    # a parameter. This connection parameter must be a real psycopg2
    # connection, not our wrapper. Here, we hook those functions to unwrap.
    import psycopg2.extensions

    orig_register_type = psycopg2.extensions.register_type

    def register_type_wrapper(type_class, conn=None):
        while isinstance(conn, ConnectionWrapper):
            # If we're passed one of our wrappers, unwrap it
            conn = conn._conn
        return orig_register_type(type_class, conn)

    psycopg2.extensions.register_type = register_type_wrapper

    return meta
