# file: tests/compiler/typechecker/statements/test_let_statement_typechecker.py

import pytest
from pydantic import TypeAdapter

from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.statement_checker import check_statement

# Create a single TypeAdapter for your Node union
node_adapter = TypeAdapter(Node)


def test_let_no_annotation_with_initializer():
    """
    let x = 42
    => x is inferred as int
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {
            "type": "VariableExpression",
            "name": "x"
        },
        # No type_annotation
        "expression": {
            "type": "LiteralExpression",
            "value": 42
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)
    # The final type of x should be inferred as "int" (assuming your default for integer literals is int).
    assert let_node.inferred_type == "int"
    assert symbol_table["x"] == "int"


def test_let_with_annotation_and_initializer():
    """
    let y: float = 3.14
    => y is 'float', matches the initializer's type
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {
            "type": "VariableExpression",
            "name": "y"
        },
        "type_annotation": "float",  # user explicitly says float
        "expression": {
            "type": "LiteralExpression",
            "value": 3.14  # defaults to 'double' or 'float' depending on your language
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)

    # If your checker unifies 3.14 -> "float" for the assignment, no error is raised.
    # If it defaults 3.14 to "double", but you allow float/double unify => float, no error.
    assert let_node.inferred_type == "float"
    assert symbol_table["y"] == "float"


def test_let_with_annotation_mismatch():
    """
    let z: int = 3.14
    => Should raise a TypeError if you can't unify 'int' and 'double/float'.
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {
            "type": "VariableExpression",
            "name": "z"
        },
        "type_annotation": "int",
        "expression": {
            "type": "LiteralExpression",
            "value": 3.14  # likely 'double'
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    # Expect a TypeError because '3.14' is not an int (unless your language auto-converts).
    with pytest.raises(TypeError, match="Cannot assign 'double' to variable of type 'int'"):
        check_statement(let_node, symbol_table)


def test_let_with_annotation_no_initializer():
    """
    let w: int
    => w is declared as 'int', no initializer.
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {
            "type": "VariableExpression",
            "name": "w"
        },
        "type_annotation": "int"
        # no expression
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)

    assert let_node.inferred_type == "int"
    assert symbol_table["w"] == "int"


def test_let_no_annotation_no_initializer():
    """
    let q
    => If your language demands either annotation or initializer, this is an error.
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {
            "type": "VariableExpression",
            "name": "q"
        },
        # no type_annotation
        # no expression
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    # Expect error because no type is declared or inferred
    with pytest.raises(TypeError, match="No type annotation or initializer for variable 'q'"):
        check_statement(let_node, symbol_table)
