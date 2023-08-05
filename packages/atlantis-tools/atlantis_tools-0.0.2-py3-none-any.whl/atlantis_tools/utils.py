from inspect import signature
from functools import wraps
import os

def typeassert(*ty_args, **ty_kwargs):
    def decorate(func):
        # If in optimized mode, disable type checking
        if not __debug__:
            return func

        # Map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            # Enforce type assertions across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError(
                            'Argument {} must be {}'.format(name, bound_types[name])
                            )
            return func(*args, **kwargs)
        return wrapper
    return decorate

def walkpath(dir_path,include_dir=True,include_file=True):
    for cur_dir_path, dir_names, file_names in os.walk(dir_path):
        if include_dir:
            for dir_name in dir_names:
                dp = os.path.join(cur_dir_path, dir_name)
                yield os.path.relpath(dp,dir_path).replace('\\','/')+"/"
        if include_file:
            for file_name in file_names:
                fp = os.path.join(cur_dir_path, file_name)
                yield os.path.relpath(fp,dir_path).replace('\\','/')