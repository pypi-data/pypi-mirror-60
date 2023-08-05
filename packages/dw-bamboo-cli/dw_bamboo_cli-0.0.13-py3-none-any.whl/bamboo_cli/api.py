def api_entry(entry, folder, params):
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
