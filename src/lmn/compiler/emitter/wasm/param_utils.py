# file: lmn/compiler/emitter/wasm/param_utils.py
import logging

# logger
logger = logging.getLogger(__name__)

def normalize_params(params):
    """
    Convert any list of (paramName, paramType) tuples into
    a list of dicts: [{"name": pName, "type_annotation": pType}, ...].
    If they're already dicts, just return as is.
    """
    if not params:
        return []

    first = params[0]
    if isinstance(first, (list, tuple)):
        # It's a list of tuples: (p_name, p_type)
        new_params = []
        for (p_name, p_type) in params:
            new_params.append({
                "name": p_name,
                "type_annotation": p_type
            })
        return new_params

    # else assume they're already dict-based
    return params
