"""Convenient access to an SQLAlchemy managed database."""

from builtins import object
__all__ = ['AutoConnectHub', 'bind_metadata', 'create_session',
    'create_session_mapper', 'commit_all', 'end_all',
    'DatabaseError', 'DatabaseConfigurationError',
    'EndTransactions', 'get_engine', 'get_metadata', 'mapper',
    'metadata', 'PackageHub', 'rollback_all', 'session',
    'session_mapper', 'set_db_uri', 'so_columns', 'so_joins', 'so_to_dict']

import sys
import time
import logging

import cherrypy
from cherrypy import request

try:
    import sqlalchemy, sqlalchemy.orm
    from sqlalchemy import MetaData
    try:
        from sqlalchemy.exc import ArgumentError, OperationalError
    except ImportError: # SQLAlchemy < 0.5
        from sqlalchemy.exceptions import ArgumentError, OperationalError
except ImportError:
    sqlalchemy = None

from peak.rules import abstract, when, NoApplicableMethods

from turbogears import config
from turbogears.util import remove_keys

log = logging.getLogger('turbogears.database')


class DatabaseError(Exception):
    """TurboGears Database Error."""


class DatabaseConfigurationError(DatabaseError):
    """TurboGears Database Configuration Error."""


# Provide support for SQLAlchemy
if sqlalchemy:

    def get_engine(pkg=None):
        """Retrieve the engine based on the current configuration."""
        bind_metadata()
        return get_metadata(pkg).bind

    def get_metadata(pkg=None):
        """Retrieve the metadata for the specified package."""
        try:
            return _metadatas[pkg]
        except KeyError:
            _metadatas[pkg] = MetaData()
            return _metadatas[pkg]

    def bind_metadata():
        """Connect SQLAlchemy to the configured database(s)."""
        if metadata.is_bound():
            return

        alch_args = dict()
        for k, v in list(config.items()):
            if 'sqlalchemy' in k:
                alch_args[k.split('.', 1)[-1]] = v

        try:
            dburi = alch_args.pop('dburi')
            if not dburi:
                raise KeyError
            metadata.bind = sqlalchemy.create_engine(dburi, **alch_args)
        except KeyError:
            raise DatabaseConfigurationError(
                "No sqlalchemy database configuration found!")
        except ArgumentError as exc:
            raise DatabaseConfigurationError(exc)

        global _using_sa
        _using_sa = True

        for k, v in list(config.items()):
            if '.dburi' in k and 'sqlalchemy.' not in k:
                get_metadata(k.split('.', 1)[0]
                    ).bind = sqlalchemy.create_engine(v, **alch_args)

    def create_session():
        """Create a session that uses the engine from thread-local metadata.

        The session by default does not begin a transaction, and requires that
        flush() be called explicitly in order to persist results to the database.

        """
        if not metadata.is_bound():
            bind_metadata()
        return sqlalchemy.orm.create_session()

    session = sqlalchemy.orm.scoped_session(create_session)

    if not hasattr(session, 'add'): # SQLAlchemy < 0.5
        session.add = session.save_or_update

    # Note: TurboGears used to set mapper = Session.mapper, but this has
    # been deprecated in SQLAlchemy 0.5.5. If it is unavailable, we emulate
    # the behaviour of the old session-aware mapper following this recipe
    # from the SQLAlchemy wiki:
    #
    # http://www.sqlalchemy.org/trac/wiki/UsageRecipes/SessionAwareMapper
    #
    # If you do not want to use the session-aware mapper, import 'mapper'
    # directly from sqlalchemy.orm. See model.py in the default quickstart
    # template for an example.
    def create_session_mapper(scoped_session=session):
        def mapper(cls, *args, **kw):
            set_kwargs_on_init = kw.pop('set_kwargs_on_init', True)
            validate = kw.pop('validate', False)
            # we accept 'save_on_init' as an alias for 'autoadd' for backward
            # compatibility, but 'autoadd' is shorter and more to the point.
            autoadd = kw.pop('autoadd', kw.pop('save_on_init', True))

            if set_kwargs_on_init and (getattr(cls,
                        '__init__', object.__init__) is object.__init__
                    or getattr(cls.__init__, '_session_mapper', False)):
                def __init__(self, **kwargs):
                    for key, value in list(kwargs.items()):
                        if validate:
                            if not hasattr(self, key):
                                raise TypeError(
                                    "Invalid __init__ argument: '%s'" % key)
                        setattr(self, key, value)
                    if autoadd:
                        session.add(self)
                __init__._session_mapper = True
                cls.__init__ = __init__
            cls.query = scoped_session.query_property()
            return sqlalchemy.orm.mapper(cls, *args, **kw)
        return mapper
    session_mapper = create_session_mapper()
    if hasattr(session, 'mapper'):
        # Old session-aware mapper
        mapper = session.mapper
    else:
        mapper = session_mapper

    _metadatas = {}
    _metadatas[None] = MetaData()
    metadata = _metadatas[None]

    try:
        import elixir
        elixir.metadata, elixir.session = metadata, session
    except ImportError:
        pass

else:
    def get_engine():
        pass
    def get_metadata():
        pass
    def bind_metadata():
        pass
    def create_session():
        pass
    session = metadata = mapper = None

bind_meta_data = bind_metadata # deprecated, for backward compatibility

hub_registry = set()

_hubs = dict() # stores the AutoConnectHubs used for each connection URI


def set_db_uri(dburi, package=None):
    """Set the database URI.

    Sets the database URI to use either globally or for a specific package.
    Note that once the database is accessed, calling it will have no effect.

    @param dburi: database URI to use
    @param package: package name this applies to, or None to set the default.

    """
    if package:
        config.update({'%s.dburi' % package: dburi})
    else:
        config.update({'sqlalchemy.dburi': dburi})


def commit_all():
    """Commit the transactions in all registered hubs (for this thread)."""
    for hub in hub_registry:
        hub.commit()


def rollback_all():
    """Rollback the transactions in all registered hubs (for this thread)."""
    for hub in hub_registry:
        hub.rollback()


def end_all():
    """End the transactions in all registered hubs (for this thread)."""
    for hub in hub_registry:
        hub.end()


@abstract()
def run_with_transaction(func, *args, **kw):
    pass


@abstract()
def restart_transaction(args):
    pass


_using_sa = False

def _use_sa(args=None):
    return _using_sa


def dispatch_exception(exception, args, kw):
    # errorhandling import here to avoid circular imports
    from turbogears.errorhandling import dispatch_error
    # Keep in mind func is not the real func but _expose
    real_func, accept, allow_json, controller = args[:4]
    args = args[4:]
    exc_type, exc_value, exc_trace = sys.exc_info()
    remove_keys(kw, ('tg_source', 'tg_errors', 'tg_exceptions'))
    try:
        output = dispatch_error(
            controller, real_func, None, exception, *args, **kw)
    except NoApplicableMethods:
        raise exc_type, exc_value, exc_trace
    else:
        del exc_trace
        return output


# include "args" to avoid call being pre-cached
@when(run_with_transaction, "_use_sa(args)")
def sa_rwt(func, *args, **kw):
    log.debug("Starting SA transaction")
    request.sa_transaction = session.begin()
    try:
        try:
            retval = func(*args, **kw)
        except (cherrypy.HTTPRedirect, cherrypy.InternalRedirect):
            # If a redirect happens, commit and proceed with redirect.
            if sa_transaction_active():
                log.debug('Redirect in active transaction - will commit now')
                session.commit()
            else:
                log.debug('Redirect in inactive transaction')
            raise
        except:
            # If any other exception happens, rollback and re-raise error
            if sa_transaction_active():
                log.debug('Error in active transaction - will rollback now')
                session.rollback()
            else:
                log.debug('Error in inactive transaction')
            raise
        # If the call was successful, commit and proceed
        if sa_transaction_active():
            log.debug('Transaction is still active - will commit now')
            session.commit()
        else:
            log.debug('Transaction is already inactive')
    finally:
        log.debug('Ending SA transaction')
        session.close()
    return retval


# include "args" to avoid call being pre-cached
@when(restart_transaction, "_use_sa(args)")
def sa_restart_transaction(args):
    log.debug("Restarting SA transaction")
    if sa_transaction_active():
        log.debug('Transaction is still active - will rollback now')
        session.rollback()
    else:
        log.debug('Transaction is already inactive')
    session.close()
    request.sa_transaction = session.begin()


def sa_transaction_active():
    """Check whether SA transaction is still active."""
    try:
        return session.is_active
    except AttributeError: # SA < 0.4.9
        try:
            return session().is_active
        except (TypeError, AttributeError): # SA < 0.4.7
            try:
                transaction = request.sa_transaction
                return transaction and transaction.is_active
            except AttributeError:
                return False


def EndTransactions():
    if _use_sa():
        try:
            session.expunge_all()
        except AttributeError: # SQLAlchemy < 0.5.1
            session.clear()
    else:
        end_all()

