# file: tests/compiler/typechecker/test_expression_checker.py

import pytest
from pydantic import TypeAdapter
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.expression_checker import check_expression

# If you have a ConversionExpression node, import it here:
# from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression

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


# -------------------------------------------------------------------
# Additional Mixed-Type Tests (Optional)
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "left_value,left_inferred,right_value,right_inferred,expected_result",
    [
        # f32 + f64 => final f64
        (2.5, "f32", 3.14, "f64", "f64"),
        # i32 + f64 => final f64
        (42, "i32", 3.14, "f64", "f64"),
        # i32 + i64 => final i64
        (100, "i32", 9999999999, "i64", "i64"),
        # f64 + f64 => final f64
        (2.71, "f64", 3.14, "f64", "f64"),
        # i32 + i32 => final i32
        (7, "i32", 13, "i32", "i32"),
    ]
)
def test_binary_expression_mixed_types(
    left_value, left_inferred,
    right_value, right_inferred,
    expected_result
):
    """
    Checks that check_expression unifies subexpressions with different numeric types.
    If your code inserts a ConversionExpression, you can check for that here.
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


@pytest.mark.skip(reason="Requires typechecker rewriting to insert ConversionExpression.")
def test_binary_expression_f32_plus_f64_inserts_conversion():
    """
    Example: If left is f32, right is f64 => result f64,
    typechecker might wrap the left side in a ConversionExpression(f32->f64).
    Uncomment if your typechecker does AST rewriting.
    """
    dict_expr = {
        "type": "BinaryExpression",
        "operator": "+",
        "left": {
            "type": "LiteralExpression",
            "value": 2.5,
            "inferred_type": "f32"
        },
        "right": {
            "type": "LiteralExpression",
            "value": 3.14,
            "inferred_type": "f64"
        }
    }
    expr_obj = node_adapter.validate_python(dict_expr)
    symbol_table = {}

    final_type = check_expression(expr_obj, symbol_table)
    assert final_type == "f64"
    assert expr_obj.inferred_type == "f64"

    # If your typechecker rewrote the left side:
    # from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
    # assert isinstance(expr_obj.left, ConversionExpression)
    # assert expr_obj.left.from_type == "f32"
    # assert expr_obj.left.to_type == "f64"
