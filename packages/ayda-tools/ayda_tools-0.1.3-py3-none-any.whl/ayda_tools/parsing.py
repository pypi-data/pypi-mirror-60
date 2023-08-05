import inspect
import importlib
from docstring_parser import parse
from .interfaces import AnnotatedData, AIModel


class ArgumentParseError(Exception):
    pass


def parse_constructor_arguments(class_type: type):
    ins = inspect.signature(class_type.__init__).parameters
    params = {}
    for p in ins:
        if p == "self":
            continue
        if ins[p].annotation == inspect._empty:
            raise ArgumentParseError(
                "Could not parse class <{}>. "
                'No annotation for parameter "{}" has been provided'.format(
                    class_type.__name__, p
                )
            )

        if ins[p].annotation.__module__ == "typing":
            name = str(ins[p].annotation)
            default = ins[p].default
        elif ins[p].annotation.__module__ != "builtins":
            name = "{}.{}".format(
                ins[p].annotation.__module__, ins[p].annotation.__name__
            )
            default = parse_constructor_arguments(ins[p].annotation)
        else:
            name = ins[p].annotation.__name__
            default = ins[p].default
        if default == inspect._empty:
            default = ins[p].annotation()
        params[p] = {"type": name, "default": default}
    for param in parse(str(class_type.__init__.__doc__)).params:
        try:
            params[param.arg_name]["description"] = param.description.replace("\n", " ")
        except KeyError:
            pass

    return {
        "class": class_type.__name__,
        "module": class_type.__module__,
        "params": params,
    }


def create_object(description: dict):
    module = importlib.import_module(description["module"])
    class_type = getattr(module, description["class"])
    params = {}
    for p in description["params"]:
        param_desc = description["params"][p]
        param_source = "default"
        if "value" in param_desc:
            param_source = "value"
        if "." in param_desc["type"] and not param_desc["type"].startswith("typing"):
            params[p] = create_object(param_desc[param_source])
        else:
            params[p] = param_desc[param_source]
    return class_type(**params)


def get_compatible_classes(module_name: str):
    importlib.import_module(module_name)
    models = list(AIModel.get_subclasses())
    datasets = list(AnnotatedData.get_subclasses())
    parsed_models = [parse_constructor_arguments(m) for m in models]
    parsed_datasets = [parse_constructor_arguments(d) for d in datasets]
    return {"models": parsed_models, "datasets": parsed_datasets}
