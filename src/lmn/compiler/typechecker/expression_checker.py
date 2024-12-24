# file: lmn/compiler/typechecker/expression_checker.py
from lmn.compiler.ast import (
    Expression,
    LiteralExpression,
    VariableExpression,
    UnaryExpression,
    BinaryExpression,
    FnExpression
)
from lmn.compiler.typechecker.utils import unify_types

def check_expression(expr: Expression, symbol_table: dict) -> str:
    """
    Return the type of the expression (e.g. "i32", "f64", etc.).
    We'll store the final type in expr.inferred_type as well.

    'expr' is a Pydantic-based node, so we can do dot access like expr.operator,
    expr.left, etc. rather than dictionary lookups.
    """
    # We rely on isinstance(...) for clarity, though you could dispatch on expr.type as well.
    if isinstance(expr, LiteralExpression):
        return check_literal_expression(expr)
    elif isinstance(expr, VariableExpression):
        return check_variable_expression(expr, symbol_table)
    elif isinstance(expr, BinaryExpression):
        return check_binary_expression(expr, symbol_table)
    elif isinstance(expr, UnaryExpression):
        return check_unary_expression(expr, symbol_table)
    elif isinstance(expr, FnExpression):
        return check_fn_expression(expr, symbol_table)
    else:
        raise NotImplementedError(f"Unsupported expression type: {expr.type}")


def check_literal_expression(lit_expr: LiteralExpression) -> str:
    """
    For a literal, if the value is a Python float => inferred_type = "f64".
    Else => "i32".
    Adjust if your language needs different rules (like int range -> i64).
    """
    val = lit_expr.value
    if isinstance(val, float):
        lit_expr.inferred_type = "f64"
        return "f64"
    else:
        lit_expr.inferred_type = "i32"
        return "i32"



def check_variable_expression(var_expr: VariableExpression, symbol_table: dict) -> str:
    """
    Looks up the variable's type in 'symbol_table'. If it's not there, raise an error.
    """
    var_name = var_expr.name
    if var_name not in symbol_table:
        raise TypeError(f"Variable '{var_name}' used before assignment.")
    vtype = symbol_table[var_name]
    var_expr.inferred_type = vtype
    return vtype


def check_binary_expression(bin_expr: BinaryExpression, symbol_table: dict) -> str:
    """
    Type check left and right sub-expressions, unify, store in 'inferred_type'.
    """
    left_type = check_expression(bin_expr.left, symbol_table)
    right_type = check_expression(bin_expr.right, symbol_table)
    result_type = unify_types(left_type, right_type)
    bin_expr.inferred_type = result_type
    return result_type


def check_unary_expression(u_expr: UnaryExpression, symbol_table: dict) -> str:
    """
    Examples:
      unary '+' => same type as operand
      unary '-' => must be numeric
      'not' => must be i32 => i32
    """
    operand_type = check_expression(u_expr.operand, symbol_table)
    op = u_expr.operator

    if op == "+":
        result_type = operand_type
    elif op == "-":
        if operand_type not in ("i32", "i64", "f32", "f64"):
            raise TypeError(f"Cannot apply '-' to {operand_type}")
        result_type = operand_type
    elif op == "not":
        if operand_type != "i32":
            raise TypeError(f"'not' requires i32 operand, got {operand_type}")
        result_type = "i32"
    else:
        raise NotImplementedError(f"Unknown unary operator: {op}")

    u_expr.inferred_type = result_type
    return result_type


def check_fn_expression(fn_expr: FnExpression, symbol_table: dict) -> str:
    """
    For a function expression/call, we check each argument's type.
    In a real compiler, you'd also unify with the function's declared param/return types.
    For now, we just say the function returns 'f64'.
    """
    for arg in fn_expr.arguments:
        check_expression(arg, symbol_table)

    # If you have a function name or something, you might do additional checks:
    # e.g. fn_name_type = check_expression(fn_expr.name, symbol_table)
    # But if fn_expr.name is just a string, you'd do something else.

    fn_expr.inferred_type = "f64"
    return "f64"
