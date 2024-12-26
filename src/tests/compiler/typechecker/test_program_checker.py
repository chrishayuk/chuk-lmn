import pytest
from lmn.compiler.typechecker.program_checker import ProgramChecker

def test_valid_program():
    """
    A 'valid' program has:
      - "type": "Program"
      - "body": a list of top-level nodes (or can be empty).
    """
    program_ast = {
        "type": "Program",
        "body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {"type": "LiteralExpression", "value": 42}
                ]
            }
        ]
    }

    checker = ProgramChecker()
    result = checker.validate_program(program_ast)
    assert result is True, "Expected a valid program"


def test_program_missing_body():
    """
    The checker defaults 'body' to [] if it's missing, 
    so this should still pass without an error.
    """
    program_ast = {
        "type": "Program"
        # No 'body' field
    }

    checker = ProgramChecker()
    result = checker.validate_program(program_ast)
    assert result is True, "Expected a valid program even if 'body' is missing"


def test_program_body_not_a_list():
    """
    If 'body' is present but not a list, the checker should raise a ValueError.
    """
    program_ast = {
        "type": "Program",
        "body": {"not": "a list"}
    }

    checker = ProgramChecker()
    with pytest.raises(ValueError) as excinfo:
        checker.validate_program(program_ast)
    assert "'body' must be a list" in str(excinfo.value)
