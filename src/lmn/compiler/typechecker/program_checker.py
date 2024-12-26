# file: src/lmn/compiler/typechecker/program_checker.py

class ProgramChecker:
    """
    Checks a top-level 'Program' AST node for required fields:
      - 'type' must be 'Program'
      - 'body' is used for top-level nodes
    """

    def validate_program(self, program_ast: dict) -> bool:
        # 1) Ensure 'type' == 'Program'
        if program_ast.get("type") != "Program":
            raise ValueError("Expected top-level 'Program'")

        # 2) 'body' should be a list; if missing, default to empty list
        body_field = program_ast.get("body")
        if body_field is not None and not isinstance(body_field, list):
            raise ValueError("'body' must be a list if present")

        if body_field is None:
            program_ast["body"] = []

        return True
