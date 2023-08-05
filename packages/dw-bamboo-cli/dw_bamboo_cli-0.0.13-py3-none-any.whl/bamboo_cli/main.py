import click
import sys
import os
import re
import inspect

from bamboo_lib.models import BasePipeline, EasyPipeline
from bamboo_lib.logger import logger


def expander(path_str):
    return os.path.expanduser(os.path.expandvars(path_str))


def parse_value(v):
    if v in ["True", "true"]:
        return True
    elif v in ["False", "false"]:
        return False
    if v.isdecimal():
        try:
            return int(v)
        except ValueError:
            return float(v)
    return v


def parse_params(raw_params, params_list=None, clazz=None):
    my_dict = {}
    plookup = {p.name: p for p in params_list} if params_list else None
    dtype_map = {my_param.name: my_param.dtype for my_param in clazz.parameter_list()}
    for p in raw_params:
        m = re.search(r'''--([^(?:\t|=)]+)="?([^"]+)"?''', p)
        try:
            key, value = m.group(1), m.group(2)
        except AttributeError:
            # Try to parse this value as flag with value set to True
            m = re.search(r"--([^(?:\t|=)]+)", p)
            key = m.group(1)
            if key in dtype_map and dtype_map[key] not in [bool, str]:
                raise ValueError("You must set a value for a non-bool parameter e.g. --{}=VALUE".format(key))
            if key in dtype_map and dtype_map[key] == bool:
                value = "True"
            else:
                value = ""
        logger.info("Received parameter with key={} and value={}".format(key, value))
        if key not in dtype_map: # default to string
            dtype_map[key] = str
        my_dict[key] = parse_value(value) if dtype_map[key] is not str else value
        if params_list and key not in plookup.keys():
            raise ValueError("Invalid parameter", key)
    if params_list:
        for missing_param in [p for p in params_list if p.required]:
            if missing_param.name not in my_dict.keys():
                raise ValueError("Missing required parameter: {}".format(missing_param.name))
    return my_dict


def get_pipeline_class(module_obj, strict_mode=False):
    candidates = []
    for _, obj in inspect.getmembers(module_obj):
        if inspect.isclass(obj) and BasePipeline in inspect.getmro(obj) and obj is not BasePipeline and obj is not EasyPipeline:
            candidates.append(obj)
    for obj in candidates:
        if isinstance(obj, EasyPipeline) and obj is not EasyPipeline:
            return obj
    if not candidates:
        raise ValueError("Module is missing appropriate pipeline class.")
    if strict_mode:
        if len(candidates) > 1:
            print(candidates)
            raise ValueError("Pipeline module contains one than one candidate class.")
    return candidates[-1]

@click.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option('--entry', prompt='Point of entry as module_name.method or simply module_name',
              help='This should be provided in the form of <module name>.<method name> or simply module_name')
@click.option('--folder', help='Folder containing the target pipeline to run', default=os.getcwd(), show_default=True)
@click.pass_context
def runner(ctx, **kwargs):
    entry = expander(kwargs['entry'])
    folder = expander(kwargs['folder'])
    sys.path.append(folder)

    if "." in entry:
        module_str, func_str = entry.rsplit(".", 1)
        module_obj = __import__(module_str)
        func_obj = getattr(module_obj, func_str)
        # try to infer pipeline class from module
        pipeline_class = get_pipeline_class(module_obj, strict_mode=True)
        param_values = parse_params(ctx.args, clazz=pipeline_class)
        return func_obj(param_values)
    else:
        module_str = entry
        module_obj = __import__(module_str)
        pipeline_class = get_pipeline_class(module_obj)
        if not hasattr(pipeline_class, "run"):
            raise ValueError(pipeline_class, "does not have a proper run(params) method")
        pipeline_obj = pipeline_class()
        # determine parameter list
        params_list = pipeline_obj.parameter_list()
        param_values = parse_params(ctx.args, params_list, clazz=pipeline_class)
        pipeline_obj.run(param_values)


if __name__ == '__main__':
    runner()
