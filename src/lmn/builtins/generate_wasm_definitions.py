# file: lmn/builtins/generate_wasm_defs.py
import json
import logging

# lmn imports
from lmn.builtins import BUILTINS

# logging
logger = logging.getLogger(__name__)

def generate_merged_wasm_json():
    """
    Gathers all 'wasm' sections from BUILTINS but flattens them
    so each function is a top-level key with { name, namespace, signature, handler, ... }.
    """
    flattened_defs = {}

    # Loop through each function name in BUILTINS
    for top_key, info in BUILTINS.items():
        # 'info' might look like:
        # {
        #   "description": "...",
        #   "typechecker": {...},
        #   "wasm": {
        #       "namespace": "env",
        #       "functions": [...]
        #   }
        # }
        wasm_block = info.get("wasm", {})
        namespace = wasm_block.get("namespace", "env")
        functions = wasm_block.get("functions", [])

        description = info.get("description")
        typechecker = info.get("typechecker")

        # If there's more than one function in the array, loop over them
        for func_def in functions:
            # e.g. func_def = { "name": "print_i32", "signature": {...}, "handler": "..." }
            fn_name = func_def["name"]
            signature = func_def["signature"]
            handler = func_def["handler"]

            # Flatten
            flattened_defs[fn_name] = {
                "name": fn_name,
                "namespace": namespace,
                "signature": signature,
                "handler": handler,
                "description": description,
                "typechecker": typechecker
            }

    # Write out the flattened definitions to a single JSON
    with open("merged_builtins.json", "w", encoding="utf-8") as f:
        json.dump(flattened_defs, f, indent=2)

    logger.debug("Wrote merged_builtins.json with flattened definitions")
