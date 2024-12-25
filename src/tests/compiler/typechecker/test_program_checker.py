import pytest
from lmn.compiler.typechecker.program_checker import ProgramChecker

def test_valid_program():
    program_ast = {
        "type": "PROGRAM",
        "globals": [
            {"type": "VAR_DECL", "name": "globalCount", "value": 0}
        ],
        "functions": [
            {
                "type": "FUNCTION_DEF",
                "name": "increment",
                "params": [],
                "body": [
                    {"type": "ASSIGN", "name": "globalCount", "value": {"type": "BINARY_EXPR", "op": "+", "lhs": "globalCount", "rhs": 1}}
                ]
            }
        ]
    }

    checker = ProgramChecker()
    result = checker.validate_program(program_ast)
    assert result is True, "Expected a valid program"

def test_program_missing_globals():
    program_ast = {
        "type": "PROGRAM",
        # 'globals' missing
        "functions": []
    }

    checker = ProgramChecker()
    with pytest.raises(KeyError) as excinfo:
        checker.validate_program(program_ast)
    assert "globals" in str(excinfo.value)

def test_program_invalid_function():
    program_ast = {
        "type": "PROGRAM",
        "globals": [],
        "functions": [
            {
                "type": "FUNCTION_DEF",
                "name": "badFunc",
                "params": ["x"],
                # Missing 'body'
            }
        ]
    }

    checker = ProgramChecker()
    with pytest.raises(ValueError) as excinfo:
        checker.validate_program(program_ast)
    assert "Function body is missing" in str(excinfo.value)
