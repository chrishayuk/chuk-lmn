# file: tests/compiler/typechecker/statements/test_return_statement_typechecker.py

import pytest
from pydantic import TypeAdapter

from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.statement_checker import check_statement

# Create a single TypeAdapter for your Node union
node_adapter = TypeAdapter(Node)

def test_return_void_ok():
    """
    If the function is declared (or inferred) as "void",
    and the ReturnStatement has no expression => OK.
    """
    symbol_table = {
        "__current_function_return_type__": "void"
    }
    dict_return = {
        "type": "ReturnStatement",
        # no 'expression' field => means 'return;'
    }

    return_node = node_adapter.validate_python(dict_return)

    # This should NOT raise an error because returning nothing in a void function is valid
    check_statement(return_node, symbol_table)

    # We can also check that the statement's inferred_type is "void"
    assert return_node.inferred_type == "void"


def test_return_value_ok():
    """
    If the function is "int" and the ReturnStatement returns an int => OK.
    """
    symbol_table = {
        "__current_function_return_type__": "int"
    }
    dict_return = {
        "type": "ReturnStatement",
        "expression": {
            "type": "LiteralExpression",
            "value": 42  # => "int"
        }
    }

    return_node = node_adapter.validate_python(dict_return)
    check_statement(return_node, symbol_table)
    # We expect no error, and the ReturnStatement should be "int"
    assert return_node.inferred_type == "int"


def test_return_value_mismatch():
    """
    If the function is declared "int", but we return a "double" => should raise TypeError.
    """
    symbol_table = {
        "__current_function_return_type__": "int"
    }
    dict_return = {
        "type": "ReturnStatement",
        "expression": {
            "type": "LiteralExpression",
            "value": 3.14  # => "double" if your language defaults float-literals to double
        }
    }

    return_node = node_adapter.validate_python(dict_return)

    with pytest.raises(TypeError, match="Return type mismatch"):
        check_statement(return_node, symbol_table)


def test_return_void_in_int_func():
    """
    If the function is declared "int", but we do 'return;' => mismatch.
    """
    symbol_table = {
        "__current_function_return_type__": "int"
    }
    dict_return = {
        "type": "ReturnStatement"
        # no expression => 'return;'
    }

    return_node = node_adapter.validate_python(dict_return)

    with pytest.raises(TypeError, match="Return type mismatch"):
        check_statement(return_node, symbol_table)


def test_return_inferred_none():
    """
    If the function has no declared return type (None),
    and the user returns an int => we infer 'int' for the function.
    """
    symbol_table = {
        "__current_function_return_type__": None
    }
    dict_return = {
        "type": "ReturnStatement",
        "expression": {
            "type": "LiteralExpression",
            "value": 99  # => "int"
        }
    }

    return_node = node_adapter.validate_python(dict_return)

    check_statement(return_node, symbol_table)
    # The statement should infer 'int'
    assert return_node.inferred_type == "int"
    # The function's return type is updated in symbol_table
    assert symbol_table["__current_function_return_type__"] == "int"


def test_return_inferred_void():
    """
    If the function's return type is None, and the user does 'return;'
    => We infer 'void'.
    """
    symbol_table = {
        "__current_function_return_type__": None
    }
    dict_return = {
        "type": "ReturnStatement"
    }

    return_node = node_adapter.validate_python(dict_return)
    check_statement(return_node, symbol_table)

    # The statement itself is 'void'
    assert return_node.inferred_type == "void"
    # The function's return type is updated to 'void'
    assert symbol_table["__current_function_return_type__"] == "void"
