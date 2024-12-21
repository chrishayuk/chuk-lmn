# tests/test_program.py

import pytest
import json
from compiler.ast.program import Program
from compiler.ast.statements.set_statement import SetStatement
from compiler.ast.expressions.literal import Literal
from compiler.ast.variable import Variable

def test_empty_program():
    prog = Program()
    result_dict = prog.to_dict()

    # Check basic structure
    assert result_dict["type"] == "Program"
    # 'body' should be an empty list if no statements
    assert isinstance(result_dict["body"], list)
    assert len(result_dict["body"]) == 0

    # Check JSON output
    result_json = prog.to_json()
    parsed = json.loads(result_json)
    assert parsed["type"] == "Program"
    assert len(parsed["body"]) == 0

def test_program_with_statements():
    prog = Program()

    # Create a single statement, e.g. 'set x 5'
    set_stmt = SetStatement(Variable("x"), Literal("5"))
    prog.add_statement(set_stmt)

    result_dict = prog.to_dict()
    assert result_dict["type"] == "Program"
    body = result_dict["body"]
    assert len(body) == 1

    # Check that the statement is a SetStatement in dict form
    assert body[0]["type"] == "SetStatement"
    assert body[0]["variable"]["name"] == "x"
    assert body[0]["expression"]["value"] == 5  # because '5' -> int 5

    # Add a second statement if you want
    # e.g. another set or a print statement...
    # Then confirm the result_dict has 2 statements, etc.
