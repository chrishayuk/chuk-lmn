# file: lmn/compiler/typechecker/expression_checker.py
from typing import Optional
from lmn.compiler.ast import (
    Expression,
    LiteralExpression,
    VariableExpression,
    UnaryExpression,
    BinaryExpression,
    FnExpression
)

# get the expression checkers
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression

# utils
from lmn.compiler.typechecker.utils import infer_literal_type


# get utilss
from lmn.compiler.typechecker.utils import unify_types, infer_literal_type

def check_expression(expr: Expression, symbol_table: dict, target_type: Optional[str] = None) -> str:
    """
    Return the type of the expression (e.g. "i32", "f64", etc.).
    We'll store the final type in expr.inferred_type as well.

    'expr' is a Pydantic-based node, so we can do dot access like expr.operator,
    expr.left, etc. rather than dictionary lookups.

    Args:
        expr: The expression to check.
        symbol_table: The current symbol table.
        target_type (Optional[str]): The expected type of the expression,
                                     especially relevant for literals in assignments.
    """
    if isinstance(expr, LiteralExpression):
        # literal expression
        return check_literal_expression(expr, target_type)  # Pass target_type
    elif isinstance(expr, VariableExpression):
        # variable expression
        return check_variable_expression(expr, symbol_table)
    elif isinstance(expr, BinaryExpression):
        # binary expression
        return check_binary_expression(expr, symbol_table)
    elif isinstance(expr, UnaryExpression):
        # unary expression
        return check_unary_expression(expr, symbol_table)
    elif isinstance(expr, FnExpression):
        # function expression
        return check_fn_expression(expr, symbol_table)
    else:
        # not supported
        raise NotImplementedError(f"Unsupported expression type: {expr.type}")


def check_binary_expression(bin_expr: BinaryExpression, symbol_table: dict) -> str:
    """
    Type check left and right sub-expressions, unify, store in 'inferred_type'.
    """
    
    # Check the types of both sub-expressions
    left_type = check_expression(bin_expr.left, symbol_table)
    right_type = check_expression(bin_expr.right, symbol_table)

    # Unify the types of both sub-expressions
    result_type = unify_types(left_type, right_type)

    # Store the inferred type in the binary expression
    bin_expr.inferred_type = result_type

    # Return the unified type
    return result_type

def check_fn_expression(fn_expr: FnExpression, symbol_table: dict) -> str:
    """
    For a function expression/call, we check each argument's type.
    In a real compiler, you'd also unify with the function's declared param/return types.
    For now, we just say the function returns 'f64'.
    """
    # iterate over each argument
    for arg in fn_expr.arguments:
        # check the argument's type
        check_expression(arg, symbol_table)

    # set the inferred type of the function expression
    fn_expr.inferred_type = "f64"

    # return the result
    return "f64"

def check_literal_expression(lit_expr: LiteralExpression, target_type: Optional[str] = None) -> str:
    """
    Determines the final type of a literal by considering the target type:
      - If expr.inferred_type is already set, keep it.
      - Otherwise, use the infer_literal_type utility, passing the target_type.
    """

    # get the inferred type
    if lit_expr.inferred_type is not None:
        return lit_expr.inferred_type
    
    # infer the literal type
    lit_expr.inferred_type = infer_literal_type(lit_expr.value, target_type)

    # return it
    return lit_expr.inferred_type

def check_unary_expression(u_expr: UnaryExpression, symbol_table: dict) -> str:
    """
    Examples:
      unary '+' => same type as operand
      unary '-' => must be numeric
      'not' => must be i32 => i32
    """

    # Check the type of the operand
    operand_type = check_expression(u_expr.operand, symbol_table)

    # Determine the type of the expression based on the operator
    op = u_expr.operator

    # operator is +
    if op == "+":
        # result is the operand type
        result_type = operand_type
    elif op == "-":
        # check the operand type is numeric
        if operand_type not in ("i32", "i64", "f32", "f64"):
            # not numeric
            raise TypeError(f"Cannot apply '-' to {operand_type}")
        
        # result is the operand type
        result_type = operand_type
    elif op == "not":
        # check the operand type is i32
        if operand_type != "i32":
            # not numeric
            raise TypeError(f"'not' requires i32 operand, got {operand_type}")
        
        # result is i32
        result_type = "i32"
    else:
        # unknown operator
        raise NotImplementedError(f"Unknown unary operator: {op}")
    
    # set the inferred type of the expression
    u_expr.inferred_type = result_type

    # return the inferred type
    return result_type

def check_variable_expression(var_expr: VariableExpression, symbol_table: dict) -> str:
    """
    Looks up the variable's type in 'symbol_table'. If it's not there, raise an error.
    """

    # Get the variable's name and type from 'symbol_table'.
    var_name = var_expr.name

    # Check that the variable is defined.
    if var_name not in symbol_table:
        raise TypeError(f"Variable '{var_name}' used before assignment.")
    
    # Get the variable's type.
    vtype = symbol_table[var_name]

    # Set the inferred type of 'var_expr' to be the same as its declared type.
    var_expr.inferred_type = vtype

    # Return the variable's type.
    return vtype