# import importlib
#
# from .exceptions import __all__ as __except_all__
# from .json_parse import __all__ as __json_parse_all__
#
# _imports = {
#     '.exceptions': __except_all__,
#     '.json_parse': __json_parse_all__
# }
# _imports_from = {n: m for m, ns in _imports.items() for n in ns}
#
#
# def __getattr__(module, name):
#     modulename = _imports_from[name]
#     if not modulename:
#         raise AttributeError(f"No attribute {name}")
#     mod = importlib.import_module(modulename)
#     value = getattr(mod, name)
#     setattr(module, name, value)
#     return value
