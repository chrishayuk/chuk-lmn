# tests/test_program.py
import json

# Import from compiler.ast (the mega-union approach), not submodules
from lmn.compiler.ast import (
    Program,
    SetStatement,
    LiteralExpression,
    VariableExpression,
)

def test_empty_program():
    prog = Program()
    result_dict = prog.to_dict()  # or prog.model_dump(by_alias=True)

    # Check basic structure
    assert result_dict["type"] == "Program"
    # 'body' should be an empty list if no statements
    assert isinstance(result_dict["body"], list)
    assert len(result_dict["body"]) == 0

    # Check JSON output
    result_json = prog.to_json()  # or however Program is defined
    parsed = json.loads(result_json)
    assert parsed["type"] == "Program"
    assert len(parsed["body"]) == 0

def test_program_with_statements():
    prog = Program()

    # Create a single statement, e.g. 'set x 5'
    set_stmt = SetStatement(
        variable=VariableExpression(name="x"),
        expression=LiteralExpression(value="5")
    )
    prog.add_statement(set_stmt)

    result_dict = prog.to_dict()  # or prog.model_dump(by_alias=True)
    assert result_dict["type"] == "Program"
    body = result_dict["body"]
    assert len(body) == 1

    # Check that the statement is a SetStatement in dict form
    assert body[0]["type"] == "SetStatement"
    # variable => a VariableExpression with name "x"
    assert body[0]["variable"]["type"] == "VariableExpression"
    assert body[0]["variable"]["name"] == "x"
    # expression => a LiteralExpression with value 5
    assert body[0]["expression"]["type"] == "LiteralExpression"
    assert body[0]["expression"]["value"] == 5  # because '5' -> int 5

    # If you add more statements, you can confirm they appear in body as well.
