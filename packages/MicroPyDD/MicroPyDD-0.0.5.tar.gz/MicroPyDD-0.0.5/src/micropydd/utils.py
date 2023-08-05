import time
import inspect

from typing import Dict, Type


def get_timestamp():
    return int(time.time() * 1000)


def object_to_dict(obj) -> Dict:
    """
    Transforms a dataclass object to a class
    :param obj:
    :return:
    """
    return dict(
        (name, getattr(obj, name)) for name in dir(obj) if
        not name.startswith('__')
        and not inspect.ismethod(getattr(obj, name)))


def dict_to_object(d: Dict, type: Type):
    """
    Transforms a dictionary to a dataclass
    :param d:
    :param type:
    :return:
    """
    def is_primitive(obj_type):
        try:
            return not(len(obj_type.__dataclass_fields__) > 0)
        except AttributeError:
            return True

    obj = {}
    for key in d.keys():
        field_type = type.__dataclass_fields__[key].type
        obj[key] = d[key] if is_primitive(field_type) else dict_to_object(d[key], field_type)
    result = type(**obj)
    return result
