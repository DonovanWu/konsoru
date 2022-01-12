def description(string):
    """
    Function decorator used when you want to show a description about your
    command in the command's help message.
    If command -> use_docstring_as_default_description is enabled in the
    config, the CLI will take docstring of the function as description
    when this is not present.

    Parameters
    ----------
    string : str
        Description string for your command.
    """
    def decorator(func):
        func.description = string
        return func
    return decorator


def parameter(name, **kwargs):
    """
    Function decorator used to provide additional information for your
    function's parameter when it is converted to command.

    Parameters
    ----------
    name : str
        Name of the parameter.
    kwargs :
        Keyword arguments to pass to ArgumentParser's add_argument() method.
    """
    def decorator(func):
        if hasattr(func, 'parameter'):
            func.parameter[name] = kwargs
        else:
            func.parameter = {name: kwargs}
        return func
    return decorator


def ignore(name, *names):
    """
    Function decorator used to ignore certain parameters of your function
    when it is converted to command. You can specify one or more parameters
    to ignore.

    Parameters
    ----------
    name : str
        Name of the parameter.
    names :
        Specify more parameters to ignore.
    """
    def decorator(func):
        all_names = set((name, ) + names)
        if hasattr(func, 'ignore'):
            func.ignore = func.ignore.union(all_names)
        else:
            func.ignore = all_names
        return func
    return decorator
