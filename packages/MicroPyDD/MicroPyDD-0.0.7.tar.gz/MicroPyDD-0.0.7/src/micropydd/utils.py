import time
import inspect

from typing import Dict, Type


def get_timestamp():
    return int(time.time() * 1000)


def is_primitive_type(obj_type):
    try:
        return not(len(obj_type.__dataclass_fields__) > 0)
    except AttributeError:
        return True


def object_to_dict(obj) -> Dict:
    """
    Transforms a dataclass object to a class
    :param obj:
    :return:
    """
    def get_value(o):
        if isinstance(o, list):
            return [get_value(x) for x in o]
        if is_primitive_type(o):
            return o
        else:
            return object_to_dict(o)
    return dict(
        (name, get_value(getattr(obj, name))) for name in dir(obj) if
        not name.startswith('__')
        and not inspect.ismethod(getattr(obj, name)))


def dict_to_object(d: Dict, type: Type, skip_unlisted_properties: bool = True):
    """
    Transforms a dictionary to a dataclass
    :param d:
    :param type:
    :param skip_unlisted_properties:
    :return:
    """
    obj = {}
    for key in d.keys():
        try:
            field_type = type.__dataclass_fields__[key].type
            if isinstance(d[key], list):
                obj[key] = [
                    dict_to_object(x, field_type.__args__[0], skip_unlisted_properties=skip_unlisted_properties)
                    for x in d[key]
                ]
            elif is_primitive_type(field_type):
                obj[key] = d[key]
            else:
                obj[key] = dict_to_object(d[key], field_type)
        except KeyError as e:
            if not skip_unlisted_properties:
                raise e
    result = type(**obj)
    return result
