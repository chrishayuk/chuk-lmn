# file: lmn/compiler/typechecker/builtins.py
BUILTIN_FUNCTIONS = {
    "llm": {
        # In this approach, we treat "prompt" as the only required parameter.
        # "model" and "temperature" are optional. 
        "required_params": {
            "prompt": "string"
        },
        "optional_params": {
            "model": "string"
        },
        "return_type": "string"
    },
}