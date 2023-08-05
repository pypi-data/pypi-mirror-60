def import_string(path):
    path_components = path.split('.')
    cls_name = path_components[-1]
    module_name = '.'.join(path_components[:-1])
    module = __import__(
        module_name, fromlist=[cls_name])
    return getattr(module, cls_name)
