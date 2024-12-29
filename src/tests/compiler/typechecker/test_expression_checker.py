# file: tests/compiler/typechecker/test_expression_checker.py

import pytest
from pydantic import TypeAdapter

from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.expression_checker import check_expression
# If your code inserts explicit conversions, uncomment this:
# from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression

# Create a single TypeAdapter for the `Node` union
node_adapter = TypeAdapter(Node)


def test_literal_expression_int():
    """
    If the literal is an integer => default is "int".
    """
    dict_expr = {
        "type": "LiteralExpression",
        "value": 42
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}

    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "int"
    assert expr_obj.inferred_type == "int"


def test_literal_expression_float():
    """
    If the literal is a float => default is "double".
    (Depending on your type system, you might choose 'float' or 'double'.)
    """
    dict_expr = {
        "type": "LiteralExpression",
        "value": 3.14
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}

    inferred = check_expression(expr_obj, symbol_table)
    # If your language treats 3.14 as a double by default, this check is correct.
    # Otherwise, you might expect "float".
    assert inferred == "double"
    assert expr_obj.inferred_type == "double"


def test_variable_expression_found():
    """
    If the symbol table has var 'x' => "double", we expect "double".
    """
    dict_expr = {
        "type": "VariableExpression",
        "name": "x"
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {"x": "double"}  # e.g. x is declared as double in the table

    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "double"
    assert expr_obj.inferred_type == "double"


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
    -(some float literal) => "double".
    """
    dict_expr = {
        "type": "UnaryExpression",
        "operator": "-",
        "operand": {
            "type": "LiteralExpression",
            "value": 42.0  # float => defaults to "double"
        }
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}

    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "double"
    assert expr_obj.inferred_type == "double"


def test_unary_not_int():
    """
    'not' + int => "int" (assuming your language treats int as boolean for 'not').
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
    assert inferred == "int"
    assert expr_obj.inferred_type == "int"


@pytest.mark.parametrize("left_val,left_is_float", [(10, False), (3.14, True)])
@pytest.mark.parametrize("right_val,right_is_float", [(2, False), (2.72, True)])
@pytest.mark.parametrize("operator", ["+", "-", "*"])
def test_binary_expression_arithmetic(left_val, left_is_float, right_val, right_is_float, operator):
    """
    If either side is a float => result is "double", else => "int".
    This test will run 3 * 2 * 2 = 12 different combos.
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

    # If either side is a float (in Python sense => e.g. 3.14),
    # we assume your type system defaults it to "double". Otherwise "int".
    expected_type = "double" if (left_is_float or right_is_float) else "int"
    assert inferred == expected_type
    assert expr_obj.inferred_type == expected_type


def test_binary_mixed_variable_and_literal():
    """
    e.g. (x + 3.14): if x => "int", unify => "double"
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
    symbol_table = {"x": "int"}  # x is declared as int

    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "double"
    assert expr_obj.inferred_type == "double"


def test_fn_expression_simple():
    """
    A naive function call => your checker might default to "double"
    or use the symbol table if declared.
    Here, the 'name' is a VariableExpression with name="myFuncName".
    """
    dict_expr = {
        "type": "FnExpression",
        "name": {
            "type": "VariableExpression",
            "name": "myFuncName"
        },
        "arguments": [
            {"type": "LiteralExpression", "value": 2},      # int => "int"
            {"type": "LiteralExpression", "value": 3.14},   # float => "double"
        ]
    }
    expr_obj = node_adapter.validate_python(dict_expr)

    # Provide a function signature in the symbol table:
    # For example, myFuncName(int, double) => double
    symbol_table = {
        "myFuncName": {
            "param_types": ["int", "double"],
            "return_type": "double"
        }
    }

    inferred = check_expression(expr_obj, symbol_table)
    assert inferred == "double"
    assert expr_obj.inferred_type == "double"


@pytest.mark.parametrize(
    "left_value,left_inferred,right_value,right_inferred,expected_result",
    [
        # float + double => final "double"
        (2.5, "float", 3.14, "double", "double"),
        # int + double => final "double"
        (42, "int", 3.14, "double", "double"),
        # int + long => final "long"
        (100, "int", 9999999999, "long", "long"),
        # double + double => final "double"
        (2.71, "double", 3.14, "double", "double"),
        # int + int => final "int"
        (7, "int", 13, "int", "int"),
    ]
)
def test_binary_expression_mixed_types(
    left_value, left_inferred,
    right_value, right_inferred,
    expected_result
):
    """
    Checks that check_expression unifies subexpressions with different numeric types.
    If your code inserts a ConversionExpression, you can test for it here.
    """
    dict_expr = {
        "type": "BinaryExpression",
        "operator": "+",
        "left": {
            "type": "LiteralExpression",
            "value": left_value,
            "inferred_type": left_inferred
        },
        "right": {
            "type": "LiteralExpression",
            "value": right_value,
            "inferred_type": right_inferred
        }
    }

    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}
    final_type = check_expression(expr_obj, symbol_table)

    assert final_type == expected_result
    assert expr_obj.inferred_type == expected_result


@pytest.mark.skip(reason="Requires rewriting to insert ConversionExpression.")
def test_binary_expression_float_plus_double_inserts_conversion():
    """
    If left is "float", right is "double" => result "double".
    Typechecker might wrap the left side in a ConversionExpression(float->double).
    Uncomment if your typechecker does AST rewriting.
    """
    dict_expr = {
        "type": "BinaryExpression",
        "operator": "+",
        "left": {
            "type": "LiteralExpression",
            "value": 2.5,
            "inferred_type": "float"
        },
        "right": {
            "type": "LiteralExpression",
            "value": 3.14,
            "inferred_type": "double"
        }
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}

    final_type = check_expression(expr_obj, symbol_table)
    assert final_type == "double"
    assert expr_obj.inferred_type == "double"

    # If your typechecker does AST insertion:
    # from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
    # assert isinstance(expr_obj.left, ConversionExpression)
    # assert expr_obj.left.from_type == "float"
    # assert expr_obj.left.to_type == "double"
