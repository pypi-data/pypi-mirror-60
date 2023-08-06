__all__ = ('yaml',)

import yaml
from pathlib import Path


def eval_value(val):
    try:
        result = val if isinstance(val, (float, int, Path)) else eval(val)
    except NameError as e:
        print(f'warnning: {str(e)}')
        result = val
    return result


def yaml_join(loader, node):
    seq = loader.construct_sequence(node)
    result = Path(seq[0])
    for sub in seq[1:]:
        result = result.joinpath(sub)
    return result


def yaml_product(loader: yaml.loader.SafeLoader, node):
    data_list = loader.construct_sequence(node)
    assert len(data_list) != 0, 'empty list'
    result = 1
    for e in data_list:
        result *= eval(e) if isinstance(e, str) else e
    return result


def yaml_ref(loader: yaml.loader.SafeLoader, node):
    ref = loader.construct_sequence(node)
    return ref[0]


def yaml_dict_ref(loader: yaml.loader.SafeLoader, node):
    dict_data, key, const_value = loader.construct_sequence(node)
    return dict_data[key] + const_value


yaml.SafeLoader.add_constructor(tag='!product', constructor=yaml_product)
yaml.SafeLoader.add_constructor(tag='!ref', constructor=yaml_ref)
yaml.SafeLoader.add_constructor(tag='!dict_ref', constructor=yaml_dict_ref)
yaml.SafeLoader.add_constructor(tag='!join', constructor=yaml_join)
