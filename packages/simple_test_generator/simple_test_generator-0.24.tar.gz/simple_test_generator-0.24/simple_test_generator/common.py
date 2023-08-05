import inspect
import os

from loguru import logger

from simple_test_generator.constants import test_data_directory

log_level = os.environ.get('PYTESTGEN_LOG_LEVEL', 'DEBUG')  # TODO: move back to TRACE


def get_test_data_filename(subdir, filename):
    return f'{test_data_directory}/{subdir}/{filename}.json'


def get_name(param):
    return param.__name__ if hasattr(param, '__name__') else ''


def get_class_that_defined_method(meth):
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth), meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)


def mergeFunctionMetadata(f, g):
    # this function was copied from Twisted core, https://github.com/racker/python-twisted-core
    # licence notice in file ../LICENCE-Twisted-core
    """
    Overwrite C{g}'s name and docstring with values from C{f}.  Update
    C{g}'s instance dictionary with C{f}'s.
    To use this function safely you must use the return value. In Python 2.3,
    L{mergeFunctionMetadata} will create a new function. In later versions of
    Python, C{g} will be mutated and returned.
    @return: A function that has C{g}'s behavior and metadata merged from
        C{f}.
    """
    try:
        g.__name__ = f.__name__
    except TypeError:
        try:
            import types

            merged = types.FunctionType(
                g.func_code, g.func_globals, f.__name__, inspect.getargspec(g)[-1], g.func_closure
            )
        except TypeError:
            pass
    else:
        merged = g
    try:
        merged.__doc__ = f.__doc__
    except (TypeError, AttributeError):
        pass
    try:
        merged.__dict__.update(g.__dict__)
        merged.__dict__.update(f.__dict__)
    except (TypeError, AttributeError):
        pass
    merged.__module__ = f.__module__
    return merged
