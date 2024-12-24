# file: tests/compiler/typechecker/test_expression_checker.py

import pytest
from pydantic import TypeAdapter
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.expression_checker import check_expression

# Create a single TypeAdapter for the `Node` union
node_adapter = TypeAdapter(Node)

def test_literal_expression_int():
    """
    If the literal is an int => 'i32'.
    """
    dict_expr = {
        "type": "LiteralExpression",
        "value": 42
    }
    # Instead of Node.model_validate(dict_expr), do:
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}
    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "i32"
    assert expr_obj.inferred_type == "i32"


def test_literal_expression_float():
    """
    If the literal is a float => 'f64'.
    """
    dict_expr = {
        "type": "LiteralExpression",
        "value": 3.14
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}
    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "f64"
    assert expr_obj.inferred_type == "f64"


def test_variable_expression_found():
    """
    If the symbol table has var 'x' => 'f64', we expect 'f64'.
    """
    dict_expr = {
        "type": "VariableExpression",
        "name": "x"
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {"x": "f64"}
    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "f64"
    assert expr_obj.inferred_type == "f64"


def test_variable_expression_not_found():
    """
    If the variable isn't in the symbol table, check_expression should raise TypeError.
    """
    dict_expr = {
        "type": "VariableExpression",
        "name": "y"
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}

    with pytest.raises(TypeError, match="Variable 'y' used before assignment"):
        check_expression(expr_obj, symbol_table)


def test_unary_minus_float():
    """
    -(some float literal) => 'f64'
    """
    dict_expr = {
        "type": "UnaryExpression",
        "operator": "-",
        "operand": {
            "type": "LiteralExpression",
            "value": 42.0
        }
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}
    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "f64"
    assert expr_obj.inferred_type == "f64"


def test_unary_not_i32():
    """
    not i32 => i32
    """
    dict_expr = {
        "type": "UnaryExpression",
        "operator": "not",
        "operand": {
            "type": "LiteralExpression",
            "value": 0
        }
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}
    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "i32"
    assert expr_obj.inferred_type == "i32"


@pytest.mark.parametrize("left_val,left_is_float", [(10, False), (3.14, True)])
@pytest.mark.parametrize("right_val,right_is_float", [(2, False), (2.72, True)])
@pytest.mark.parametrize("operator", ["+", "-", "*"])
def test_binary_expression_arithmetic(left_val, left_is_float, right_val, right_is_float, operator):
    """
    If either side is float => f64, else => i32.
    """
    dict_expr = {
        "type": "BinaryExpression",
        "operator": operator,
        "left": {
            "type": "LiteralExpression",
            "value": left_val
        },
        "right": {
            "type": "LiteralExpression",
            "value": right_val
        }
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}
    inferred = check_expression(expr_obj, symbol_table)

    expected_type = "f64" if (left_is_float or right_is_float) else "i32"
    assert inferred == expected_type
    assert expr_obj.inferred_type == expected_type


def test_binary_mixed_variable_and_literal():
    """
    e.g. (x + 3.14): x => i32, unify => f64
    """
    dict_expr = {
        "type": "BinaryExpression",
        "operator": "+",
        "left": {
            "type": "VariableExpression",
            "name": "x"
        },
        "right": {
            "type": "LiteralExpression",
            "value": 3.14
        }
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {"x": "i32"}
    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "f64"
    assert expr_obj.inferred_type == "f64"


def test_fn_expression_simple():
    """
    A naive function call => always returns 'f64'.
    """
    dict_expr = {
        "type": "FnExpression",
        "name": {
            "type": "LiteralExpression",
            "value": "myFuncName"
        },
        "arguments": [
            {"type": "LiteralExpression", "value": 2},      # i32
            {"type": "LiteralExpression", "value": 3.14},   # f64
        ]
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}
    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "f64"
    assert expr_obj.inferred_type == "f64"
