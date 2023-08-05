import functools
import inspect
import os
from _collections_abc import list_iterator
from glob import glob
from types import GeneratorType
from typing import TextIO

from _pytest.python import Metafunc
from loguru import logger

from simple_test_generator.common import get_name, get_class_that_defined_method, mergeFunctionMetadata
from simple_test_generator.constants import test_data_directory


class Scenario:
    def __init__(self, module, argnames, args, kwargs, expected):
        self.module = module
        self.argnames = argnames
        self.args = args
        self.kwargs = kwargs

        if isinstance(expected, list_iterator):
            # because jsonpickle serialises things like generators as "list iterators"
            expected = list(expected)
        self.expected = expected


def deserialise(f):
    return deserialise_json(f)


def deserialise_json(f: TextIO):
    import jsonpickle

    contents = f.read()
    return jsonpickle.loads(contents)


def transform_function(f):
    if getattr(f, 'pytestgen_decorated_with_record_test_data', False):
        # raise Exception('Already decorated')
        return f

    clazz = get_class_that_defined_method(f)

    arg_signature = inspect.getfullargspec(f).args
    is_cls_function = clazz and arg_signature and arg_signature[0] == 'cls'

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if is_cls_function:
            first_arg_is_cls = len(args) and not isinstance(list(args)[0], clazz) or not len(args)
            if first_arg_is_cls:
                args = remove_first_argument(args)
        return_value = f(*args, **kwargs)
        if isinstance(return_value, GeneratorType):
            # generators aren't really comparable, so we compare lists instead
            return list(return_value)
        return return_value

    def remove_first_argument(args):
        return tuple(list(args)[1:])

    wrapper.pytestgen_decorated_with_record_test_data = True
    return wrapper


def load_data_file(filename):
    cases = []
    with open(filename, 'r') as f:
        try:
            data = deserialise(f)
        except Exception as e:
            logger.error(f'Error loading data file {filename}')
            logger.error(e)
            return
    fn = data['function']
    if not fn:
        logger.warning(f'Function was not properly loaded from {filename}')
        return
    module = data['module']
    function_name = fn.__name__
    for item in data['test_cases']:
        case = Scenario(module, data['argnames'], item['args'], item['kwargs'], item['expected'])
        cases.append(case)

    clazz = data['class']
    fn = getattr(clazz or module, function_name)
    new_item = mergeFunctionMetadata(fn, transform_function(fn))
    setattr(module, fn.__name__, new_item)

    is_non_class_method = True
    if clazz and data['argnames']:
        is_non_class_method = True  # data['argnames'][0] != 'cls'
        # if not is_non_class_method:
        #   logger.debug(case.args)

    return (
        module,
        clazz,
        [(new_item, x.args if is_non_class_method else x.args[1:], x.kwargs, x.expected) for x in cases],
    )


def parametrize_stg_tests(metafunc: Metafunc):
    if metafunc.definition.name != 'test_simple_test_generator_test_cases':
        return
    sep = os.sep
    path_list = sorted(glob(f'{test_data_directory}{sep}*{sep}**{sep}*.json', recursive=True))
    all_test_data = []
    all_ids = []
    for data_file_path in path_list:
        split = data_file_path.split(sep)
        function_name = split[-2]
        try:
            tuple_result = load_data_file(data_file_path)
            if tuple_result:
                module, clazz, test_cases = tuple_result
            else:
                continue
        except Exception as e:
            logger.error(f'Could not load data file {data_file_path}')
            logger.error(e)
            raise e
        module_name = get_name(module)
        class_name = get_name(clazz)
        class_or_module_name = module_name if module_name != class_name else f'{module_name}.{class_name}'
        ids = [f'{class_or_module_name}-{function_name}'] * len(test_cases)
        all_test_data.extend(test_cases)
        all_ids.extend(ids)
    metafunc.parametrize(['fn', 'args', 'kwargs', 'expected'], all_test_data, ids=all_ids)
