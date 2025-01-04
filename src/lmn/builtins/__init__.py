import os
import json

# Empty dictionary to store the flattened builtins
BUILTINS = {}

# The directory containing this __init__.py file
dir_path = os.path.dirname(__file__)

def _flatten_functions_in_block(block: dict) -> dict:
    """
    Given a dictionary block like:
        {
          "description": "...",
          "typechecker": { ... },
          "wasm": {
            "namespace": "env",
            "functions": [
              {
                "name": "print_i32",
                "signature": { ... },
                "handler": "..."
              }
            ]
          }
        }
    Return a dict where each function is mapped to a flattened object like:
        {
          "print_i32": {
            "name": "print_i32",
            "namespace": "env",
            "signature": { ... },
            "handler": "...",
            "description": "...",
            "typechecker": { ... }
          }
        }
    """
    flattened = {}
    description = block.get("description")
    typechecker = block.get("typechecker")
    wasm_block = block.get("wasm", {})
    namespace = wasm_block.get("namespace", "env")
    functions = wasm_block.get("functions", [])

    for func_def in functions:
        fn_name = func_def["name"]
        # Flatten
        flattened[fn_name] = {
            "name": fn_name,
            "namespace": namespace,
            "signature": func_def["signature"],
            "handler": func_def["handler"],
            "description": description,
            "typechecker": typechecker
        }

    return flattened

# Iterate over all JSON files in the directory
for filename in os.listdir(dir_path):
    if filename.endswith(".json"):
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # data might look like:
            # {
            #   "print_i32": {
            #       "description": "...",
            #       "typechecker": { ... },
            #       "wasm": {
            #          "namespace": "env",
            #          "functions": [
            #             { "name": "print_i32", "signature": {...}, "handler": "..." }
            #          ]
            #       }
            #   },
            #   "print_f32": { ... }
            # }

            # We need to flatten each top-level key
            for top_key, block in data.items():
                flattened_dict = _flatten_functions_in_block(block)

                # Merge each flattened function into BUILTINS
                # If "print_i32" is the function name, it becomes BUILTINS["print_i32"] = {...}
                BUILTINS.update(flattened_dict)

# Now BUILTINS is a dict of shape:
# {
#   "print_i32": {
#     "name": "print_i32",
#     "namespace": "env",
#     "signature": { ... },
#     "handler": "...",
#     "description": "...",
#     "typechecker": { ... }
#   },
#   "print_i64": { ... },
#   ...
# }

