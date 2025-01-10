# file: lmn/compiler/typechecker/builtin_checker.py
from lmn.builtins import BUILTINS

def typecheck_call(func_name, user_params: dict):
    """
    Example usage:
       validated_params, return_type = typecheck_call("llm", {"prompt": "Hello!"})
    This function:
      1) Looks up func_name in BUILTINS.
      2) Validates user_params against the built-in's 'typechecker' info.
      3) Returns (validated_params, return_type).
    """

    # 1) Check if the function exists in built-ins
    if func_name not in BUILTINS:
        raise TypeError(f"Unknown built-in function: {func_name}")

    # 2) Grab the typechecker info: 'params' + 'return_type'
    tc_info = BUILTINS[func_name]["typechecker"]
    params_def = tc_info["params"]          # e.g. [ { "name":"prompt", "type":"string", ...}, ... ]
    return_type = tc_info["return_type"]    # e.g. "string"

    # 3) Prepare a dict for validated parameters
    validated_params = {}

    # 4) Loop through each param definition
    for param_def in params_def:
        name = param_def["name"]                      # param name, e.g. "prompt"
        ptype = param_def["type"]                     # param type, e.g. "string"
        required = param_def.get("required", False)   # required?
        default = param_def.get("default", None)      # default value if any

        # Check if the param is missing in user_params
        if name not in user_params:
            if required and default is None:
                # Missing required param => error
                raise TypeError(f"Missing required param '{name}' for '{func_name}'")
            else:
                # Use default if given, else None
                validated_params[name] = default
        else:
            # Optionally: we could validate user_params[name] is the correct type
            # For now, we just store it
            validated_params[name] = user_params[name]

    # 5) Return the final dictionary of validated params and the function’s return_type
    return validated_params, return_type
