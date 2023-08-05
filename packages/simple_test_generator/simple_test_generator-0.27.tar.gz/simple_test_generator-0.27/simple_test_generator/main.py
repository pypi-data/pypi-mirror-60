import functools
import inspect
import os
import sys
from fnmatch import fnmatch
from os.path import abspath
from threading import Thread
from typing import List, Dict

from loguru import logger

from simple_test_generator.common import (
    get_test_data_filename,
    get_name,
    get_class_that_defined_method,
    mergeFunctionMetadata,
    log_level,
)
from simple_test_generator.constants import test_data_directory, filename_count_limit, test_filename, test_directory

user_function = os.environ.get('PYTESTGEN_FUNCTION', 'main')
invocation_limit_per_function = int(os.environ.get('PYTESTGEN_TEST_CASE_COUNT_PER_FUNCTION', '5'))
serialisation_depth = int(os.environ.get('PYTESTGEN_SERIALISATION_DEPTH', '500'))
filesize_limit = int(os.environ.get('PYTESTGEN_FILESIZE_LIMIT_MB', '5')) * 1024 * 1024
allow_all_modules = 'PYTESTGEN_ALLOW_ALL_MODULES' in os.environ
include_modules = os.environ.get('PYTESTGEN_INCLUDE_MODULES', '').split(',')
exclude_modules = os.environ.get('PYTESTGEN_EXCLUDE_MODULES', '').split(',')
# TODO: how to load files saved at paths like test-data/2019.1/config/plugins/python/helpers/pycharm/_jb_runner_tools.py/_parse_parametrized/01.json ?
# TODO: try pickling with dill to try to serialise more types, e.g functions
# TODO: how to use this with tox projects? because tox writes files in temporary virtual envs
# TODO: test with kwargs and optional parameters
# TODO: add real-world examples of running real projects with it (like pytest, httpie, jsonpickle, ansible, pipenv itself!)
# TODO: show how to use with web frameworks like Django
# TODO: why not simply deepcopy function instead of merge metadata?
# TODO: document how users can add data according to my convention
# TODO: test well self, cls, args and kwargs altogether. include calls to each other
# TODO: skip editing conftest or functions in it that start with pytest_
# TODO: how are async functions handled?
# TODO: seemingly duplicate files are being written:
# botocore.model/ServiceModel/resolve_shape_ref/01.json (636841)
# botocore.model/ServiceModel/resolve_shape_ref/02.json (636841)
# botocore.model/ServiceModel/resolve_shape_ref/03.json (636841)
# botocore.model/ServiceModel/resolve_shape_ref/04.json (636841)
# botocore.model/ServiceModel/resolve_shape_ref/05.json (636841)
# botocore.model/ServiceModel/resolve_shape_ref/06.json (636841)


def fn_description(f):
    return f'{f.__module__}.{f.__qualname__}'


def log_call(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug(f'Entering {f}')
        return_value = f(*args, **kwargs)
        logger.debug(f'Exiting {f}')

        return return_value

    return wrapper


def log_error(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f'Error in {f} with {args[:2]}: {e}, skipping test cases for function.')

    return wrapper


def group_by_function(invocations: List) -> Dict[object, List]:
    result = {}
    for invocation in invocations:
        f = invocation['f']
        if f not in result:
            result[f] = []
        if len(result[f]) >= invocation_limit_per_function:
            continue
        if invocation in result[f]:
            continue
        if is_function(invocation['return_value']):
            logger.log(log_level, 'Functions that return functions are not supported; skipping.')
            continue
        result[f].append(invocation)
    return result


def is_function(param):
    return inspect.isroutine(param)
    # import types
    #
    # return isinstance(
    #     param, (types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.BuiltinMethodType)
    # )


def is_site_package(module):
    return 'site-packages' in (get_dict(module).get('__file__') or {})


def exclude_importers(module):
    loader = get_dict(module).get('__loader__')
    loader_type = type(loader)
    if hasattr(loader_type, '__name__'):
        name = loader_type.__name__
    elif hasattr(loader, 'name'):
        name = loader.name
    if loader:
        qualified_name = loader_type.__module__ + '.' + name
    else:
        qualified_name = ''
    return qualified_name.endswith('._SixMetaPathImporter')


def is_system_package(module):
    from importlib._bootstrap import BuiltinImporter, FrozenImporter

    dict__ = get_dict(module)
    loader = dict__.get('__loader__')
    name__ = get_name(module)
    return (
        loader in [BuiltinImporter, FrozenImporter]
        or (
            hasattr(module, '__file__')
            and (module.__file__ is not None)
            and f"python{sys.version_info.major}.{sys.version_info.minor}/{(module.__package__ or '').replace('.', '/')}"
            in module.__file__
        )
        or name__.startswith('typing.')
    )


def get_dict(module):
    if hasattr(module, '__dict__'):
        return module.__dict__
    return {}


def get_module(name):
    return sys.modules.get(name)


def get_loaded_modules():
    import sys

    all_modules = []
    for name, module in sys.modules.items():
        all_modules.append((name, module))
    return all_modules


def singleton(cls):
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls


def save_example_scripts():
    logger.info(f'Saving example scripts under {test_directory}')
    with open(f'{test_directory}/{test_filename}', 'w') as f:
        f.write(
            f"""
def test_simple_test_generator_test_cases(fn, args, kwargs, expected):
    ""\"See {test_data_directory} directory for test cases\"""
    actual = fn(*args, **kwargs)
    assert actual == expected
"""
        )

    with open(f'{test_directory}/conftest-simple-test-generator-runtime.py', 'w') as f:
        f.write(
            f"""
def pytest_generate_tests(metafunc):
    from simple_test_generator import parametrize_stg_tests

    parametrize_stg_tests(metafunc)


"""
        )

    with open(f'{test_directory}/conftest-simple-test-generator-record.py', 'w') as f:
        f.write(
            f"""from simple_test_generator import Recorder


def pytest_runtestloop(session):
    Recorder().enter()


def pytest_sessionfinish(session, exitstatus):
    Recorder().exit()


"""
        )


def print_invocation_group_summary(group):
    for fn, invocations in group.items():
        logger.info(f'{fn.__module__}.{fn.__name__} got {len(invocations)} invocations')


def get_file(module):
    return module.__file__ if hasattr(module, '__file__') and module.__file__ else ''


def is_test_class(clazz):
    import unittest

    return issubclass(clazz, unittest.TestCase)


@singleton
class Recorder:
    def __init__(self):
        logger.info('creating instance of recorder')
        self.invocations = []

    def add_invocation(self, return_value, f, args, kwargs):
        i = {'return_value': return_value, 'f': f, 'args': args, 'kwargs': kwargs}
        self.invocations.append(i)

    def __enter__(self):
        self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()

    def edit_functions(self, items, module):
        for fn_name, fn in items:
            if fn == self.edit_functions:
                continue
            fn_module = get_module(fn.__module__)
            if not self.is_module_allowed(fn_module):
                logger.log(log_level, f'skipping {fn_module}.{fn.__name__}')
                continue
            logger.log(log_level, f'editing {fn_name} {module} ({fn.__module__}).{fn.__name__}')
            new_item = mergeFunctionMetadata(fn, self.record_test_data(fn))
            setattr(module, fn.__name__, new_item)

    def record_test_data(self, f):
        this = self
        logger.log(log_level, f)
        if getattr(f, 'pytestgen_decorated_with_record_test_data', False):
            return f
        if f in [self.record_test_data]:
            return f

        clazz = get_class_that_defined_method(f)
        arg_signature = inspect.getfullargspec(f).args
        is_cls_function = clazz and arg_signature and arg_signature[0] == 'cls'

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            logger.log(log_level, f'wrapped {f}')
            if is_cls_function:
                # args = tuple([clazz] + list(args))
                if len(args) and not isinstance(list(args)[0], clazz):
                    args = add_class_object_as_arg(args)
                elif not len(args):
                    args = tuple([clazz] + list(args))
            # try:
            return_value = f(*args, **kwargs)
            # except:
            #     args = tuple([get_class_that_defined_method(f)] + list(args))
            #     return_value = f(*args, **kwargs)

            this.add_invocation(return_value, f, args, kwargs)
            return return_value

        def add_class_object_as_arg(args):
            return tuple([clazz] + list(args))

        wrapper.pytestgen_decorated_with_record_test_data = True
        return wrapper

    def enter(self):
        self.edit_module_level_functions()
        self.edit_module_level_classes()
        logger.log(log_level, 'Start recording invocations')

    def edit_module_level_classes(self):
        for name, module in get_loaded_modules():
            logger.log(log_level, f'loading {name}')
            if not self.is_module_allowed(module):
                continue
            try:
                classes = inspect.getmembers(module, inspect.isclass)
            except Exception as e:
                logger.warning(f'Failed getting members for module {module}, skipping')
                logger.error(e)
                continue
            # TODO: patch parent class methods
            # TODO: what if a module imported a class from another module?

            for class_name, clazz in classes:
                # clazz = class_tuple[1]
                if clazz == self.__class__:
                    continue
                if issubclass(clazz, Thread):
                    logger.log(log_level, 'skipping thread classes')
                    continue
                if not self.is_module_allowed(get_module(clazz.__module__)):
                    continue
                self.edit_class_function(class_name, clazz)

    def edit_class_function(self, class_name, clazz):
        fn_name: str
        for fn_name, fn in clazz.__dict__.items():
            if not is_function(fn):
                continue
            if fn_name.startswith('__'):  # and fn_name != '__init__':
                continue
            if get_module(fn) == 'tests' and fn_name in ['tearDown', 'setUp']:
                continue
            if inspect.isbuiltin(fn):
                continue
            if is_test_class(clazz) and fn_name in ['setUp', 'tearDown']:
                logger.log(log_level, f'Skipping test function in class {clazz}')
                continue
            logger.log(log_level, f'editing {get_module(clazz.__module__)}.{class_name}.{fn_name}')
            if not hasattr(fn, '__name__') and hasattr(fn, '__func__'):
                # logger.log(log_level, dir(fn.__func__))
                fn = fn.__func__
            try:
                new_item = mergeFunctionMetadata(fn, self.record_test_data(fn))
            except Exception as e:
                logger.error(e)
                raise  # continue
            # TODO: if not being able to recreate method properly, can check how boto3 does it
            try:
                setattr(clazz, fn_name, new_item)
            except Exception as e:
                logger.error(e)
                continue

    def edit_module_level_functions(self):
        for name, module in get_loaded_modules():
            logger.log(log_level, f'loading {name}')
            if not self.is_module_allowed(module):
                continue
            try:
                items = inspect.getmembers(module, inspect.isfunction)
            except Exception as e:
                # I saw this could happen when in debug mode
                logger.warning(f'Failed getting members for module {module}, skipping')
                logger.error(e)
                continue
            logger.log(log_level, f'allowing module {module}')
            self.edit_functions(items, module)

    @staticmethod
    def match_in_modules(module_name, modules):
        for item in modules:
            if fnmatch(module_name, item):
                return True

    @classmethod
    def is_module_explicitly_allowed(cls, module_name):
        return cls.match_in_modules(module_name, include_modules)

    @classmethod
    def is_module_explicitly_disallowed(cls, module_name):
        return cls.match_in_modules(module_name, exclude_modules)

    def is_module_allowed(self, module):
        if allow_all_modules:
            return True
        module_name = get_name(module)
        if module_name == '__main__':
            logger.log(log_level, 'Skipping __main__ module as main module will be a different one at run time')
            return
        if self.is_module_explicitly_disallowed(module_name):
            logger.log(log_level, f'Module explicitly disallowed: {module}')
            return
        if self.is_module_explicitly_allowed(module_name):
            logger.log(log_level, f'Module explicitly allowed: {module}')
            return True
        if module_name.startswith('simple_test_generator'):
            logger.log(log_level, 'Excluding the recorder itself')
            return
        if module_name.startswith('py.'):
            logger.log(log_level, 'Skipping modules starting with py.')
            return
        # if 'pytest' in module_name:
        #     logger.log(log_level, 'Excluding pytest and its plugins')
        #     return
        if 'pydev' in module_name or 'py.builtin' in module_name or 'helpers/pycharm/' in get_file(module):
            logger.log(log_level, 'Excluding debugger modules')
            return
        if is_site_package(module):
            logger.log(log_level, f'excluding site package {module}')
            return
        if exclude_importers(module):
            logger.log(log_level, f'excluding importer {module}')
            return
        if is_system_package(module):
            logger.log(log_level, f'excluding system module {module}')
            return
        return True

    def exit(self):
        logger.log(log_level, f'Stopped recording invocations, got {len(self.invocations)} of them.')
        invocation_group = group_by_function(self.invocations)
        print_invocation_group_summary(invocation_group)
        save_example_scripts()
        self.save_test_data(invocation_group)

    def save_test_data(self, invocation_group):
        for fn, invocations in invocation_group.items():
            module = inspect.getmodule(fn)
            if not self.is_module_allowed(module):
                # maybe it was loaded afterwards! TODO: How to handle such cases?
                logger.log(log_level, f'{module} was previously disallowed')
                continue
            module_name = fn.__module__
            clazz = get_class_that_defined_method(fn)
            logger.log(log_level, f'{module_name}.{get_name(fn)}')
            parameters = inspect.signature(fn).parameters
            argnames = list(parameters.keys())

            test_cases = [
                {'args': x['args'], 'kwargs': x['kwargs'], 'expected': x['return_value']} for x in invocations
            ]
            write_data_file(module_name, module, clazz, fn, test_cases, argnames)


@log_error
def write_data_file(module_name, module, clazz, fn, test_cases, argnames):
    function_name = fn.__name__
    if not test_cases:
        return
    class_or_module_name = get_name(clazz) or module_name
    subdir = f'{module_name}/{class_or_module_name}/{function_name}'
    create_directory(subdir)

    success = False
    contents = serialise(argnames, module, clazz, fn, test_cases)
    if len(contents) > filesize_limit:
        logger.log(log_level, 'Content is bigger than configured filesize limit')
        return
    for i in range(filename_count_limit):
        filename = get_test_data_filename(subdir, f'{i+1:02}')
        filepath = abspath(filename)
        if os.path.exists(filepath):
            logger.log(log_level, f'{filename} already exists, skipping.')
            continue
        logger.log(log_level, f'Writing data file at {filepath} ({len(contents)})')
        with open(filepath, 'w') as f:
            f.write(contents)
            success = True
            break
    if not success:
        logger.error(
            f'Could not save test data for function {module_name}.{function_name}, e.g at {filename}. Merge existing test case files or delete them and try again.'
        )


def serialise(argnames, module, clazz, fn, test_cases):
    return serialise_json(argnames, module, clazz, fn, test_cases)


def serialise_json(argnames, module, clazz, fn, test_cases):
    import jsonpickle as json

    return json.dumps(
        {'test_cases': test_cases, 'argnames': argnames, 'class': clazz, 'module': module, 'function': fn},
        max_depth=serialisation_depth,
    )


def create_directory(sub_dir):
    from os import makedirs

    try:
        makedirs(os.path.join(test_data_directory, sub_dir))
    except Exception as e:
        logger.log(log_level, e)


def print_results(by_time):
    for item in by_time:
        logger.info(fn_description(item[0]) + f',invoked={item[2]} times, total={item[1] / 1_000_000}ms')
