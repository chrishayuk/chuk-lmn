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
        "variable": {"type": "VariableExpression", "name": "x"},
        "expression": {"type": "LiteralExpression", "value": 42}
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)

    # If your code infers x => "int"
    assert let_node.inferred_type == "int"
    assert symbol_table["x"] == "int"


def test_let_with_annotation_and_initializer():
    """
    let y: float = 3.14
    => If your code treats 3.14 as "double",
       and does NOT unify 'double' -> 'float',
       we expect the final type to remain "double".
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "y"},
        "type_annotation": "float",
        "expression": {"type": "LiteralExpression", "value": 3.14}
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)

    # If your code defaults 3.14 => "double" and doesn't unify to "float"
    # we expect let_node.inferred_type == "double".
    # So let's verify:
    assert let_node.inferred_type == "float"
    assert symbol_table["y"] == "float"



def test_let_with_annotation_mismatch():
    """
    let z: int = 3.14
    => Should raise TypeError if you can't unify 'int' and 'double'.
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "z"},
        "type_annotation": "int",
        "expression": {"type": "LiteralExpression", "value": 3.14}
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    # If your code says "Cannot assign 'double' to var of type 'int'" => match that
    with pytest.raises(TypeError, match="Cannot assign 'double' to var of type 'int'"):
        check_statement(let_node, symbol_table)


def test_let_with_annotation_no_initializer():
    """
    let w: int
    => w is declared as 'int', no initializer.
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "w"},
        "type_annotation": "int"
        # no expression
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)

    # w => "int"
    assert let_node.inferred_type == "int"
    assert symbol_table["w"] == "int"


def test_let_no_annotation_no_initializer():
    """
    let q
    => If your language demands either annotation or initializer, error.
    """
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "q"},
        # no type_annotation
        # no expression
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    # If your code says "No type annotation or initializer for 'q' in let statement."
    with pytest.raises(TypeError, match="No type annotation or initializer for 'q' in let statement."):
        check_statement(let_node, symbol_table)


# -----------------------------
# Additional Array Tests
# -----------------------------

def test_let_inferred_string_array():
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "colors"},
        "expression": {
            "type": "JsonLiteralExpression",
            "value": ["red", "green", "blue"]
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)

    # If your updated logic infers an all-string JSON array => "string[]"
    assert let_node.inferred_type == "string[]"
    assert symbol_table["colors"] == "string[]"


def test_let_inferred_int_array():
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "nums"},
        "expression": {
            "type": "JsonLiteralExpression",
            "value": [1, 2, 3]
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)
    assert let_node.inferred_type == "int[]"
    assert symbol_table["nums"] == "int[]"


def test_let_inferred_mixed_json_array():
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "data"},
        "expression": {
            "type": "JsonLiteralExpression",
            "value": [1, "two", 3]
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)
    # Mixed => "json"
    assert let_node.inferred_type == "json"
    assert symbol_table["data"] == "json"


def test_let_explicit_string_array():
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "names"},
        "type_annotation": "string[]",
        "expression": {
            "type": "JsonLiteralExpression",
            "value": ["Alice", "Bob"]
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)

    assert let_node.inferred_type == "string[]"
    assert symbol_table["names"] == "string[]"


def test_let_explicit_float_array():
    dict_ast = {
        "type": "LetStatement",
        "variable": {"type": "VariableExpression", "name": "floats"},
        "type_annotation": "float[]",
        "expression": {
            "type": "JsonLiteralExpression",
            "value": [1, 2.5, 3]
        }
    }
    let_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    check_statement(let_node, symbol_table)
    assert let_node.inferred_type == "float[]"
    assert symbol_table["floats"] == "float[]"
