# file: src/lmn/compiler/typechecker/program_checker.py

class ProgramChecker:
    """
    Checks a top-level 'PROGRAM' AST node for required fields:
      - "globals" must exist
      - "functions" must exist
      - each function must have a "body"
    Returns True if all checks pass, otherwise raises errors that match your tests.
    """

    def validate_program(self, program_ast: dict) -> bool:
        # 1) Check top-level type is 'PROGRAM'
        if program_ast.get("type") != "PROGRAM":
            raise ValueError("Expected top-level 'PROGRAM'")

        # 2) Check that 'globals' field exists
        if "globals" not in program_ast:
            raise KeyError("globals")

        # 3) Check that 'functions' field exists
        if "functions" not in program_ast:
            raise KeyError("functions")

        # 4) Validate each function in the 'functions' list
        for func_def in program_ast["functions"]:
            # If "body" is missing, raise ValueError
            if "body" not in func_def:
                raise ValueError("Function body is missing")

            # (Optional) If you want to ensure the function's "type" is 'FUNCTION_DEF':
            # if func_def.get("type") != "FUNCTION_DEF":
            #     raise ValueError("Expected 'FUNCTION_DEF' in functions array")

        # If all checks pass, return True
        return True
