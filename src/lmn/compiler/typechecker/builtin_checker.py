# file: lmn/compiler/typechecker/builtin_checker.py
from lmn.builtins import BUILTINS

def typecheck_call(func_name, user_params: dict):
    """
    Example usage: typecheck_call("llm", {"prompt": "Hello!"})
    """

    # check if the function exists
    if func_name not in BUILTINS:
        # raise an error
        raise TypeError(f"Unknown built-in function: {func_name}")

    # Grab the typechecker info
    tc_info = BUILTINS[func_name]["typechecker"]
    params_def = tc_info["params"]
    return_type = tc_info["return_type"]

    # initialize the final dictionary of validated params
    validated_params = {}

    # loop through the params definition
    for param_def in params_def:
        # Extract the param details
        name = param_def["name"]
        ptype = param_def["type"]
        required = param_def.get("required", False)
        default = param_def.get("default", None)

        # Check if the param is missing
        if name not in user_params:
            # Check if the param is required
            if required and default is None:
                # Raise an error
                raise TypeError(f"Missing required param '{name}' for '{func_name}'")
            else:
                # Use default if provided
                validated_params[name] = default
        else:
            # Optionally validate type (e.g., check if it's string/int)
            validated_params[name] = user_params[name]

    # Return the final dictionary of validated params and the return type
    return validated_params, return_type

