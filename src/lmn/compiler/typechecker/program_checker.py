# file: src/lmn/compiler/typechecker/program_checker.py
import logging

# get the logger
logger = logging.getLogger(__name__)

class ProgramChecker:
    """
    Checks a top-level 'Program' AST node for required fields:
      - 'type' must be 'Program'
      - 'body' is used for top-level nodes
    """

    def validate_program(self, program_ast: dict) -> bool:
        # 1) Ensure 'type' == 'Program'
        #
        # Log the entire AST (or a summary) for debugging:
        logger.debug("Starting validate_program with AST: %s", program_ast)
        
        if program_ast.get("type") != "Program":
            # Use an error log to highlight a serious issue before raising an exception.
            logger.error("Expected top-level 'Program', but got: %r", program_ast.get("type"))
            raise ValueError("Expected top-level 'Program'")

        # 2) 'body' should be a list; if missing, default to empty list
        body_field = program_ast.get("body")

        # Debug log to show what 'body' looks like right now.
        logger.debug("Found 'body' field: %r", body_field)

        if body_field is not None and not isinstance(body_field, list):
            logger.error("'body' must be a list if present; got: %r", type(body_field).__name__)
            raise ValueError("'body' must be a list if present")

        if body_field is None:
            logger.debug("'body' is missing; setting it to an empty list.")
            program_ast["body"] = []

        # If we reach here, the structure is valid.
        logger.debug("Finished validate_program: 'Program' node is valid.")
        return True
