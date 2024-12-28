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
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
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
    If we discover a mismatch that requires up/down-casting (e.g. f32 + f64 => f64),
    we insert a ConversionExpression on the side that needs promotion/demotion.
    """

    # 1) Check the types of both sub-expressions
    left_type = check_expression(bin_expr.left, symbol_table)
    right_type = check_expression(bin_expr.right, symbol_table)

    # 2) Unify to get the final result type
    result_type = unify_types(left_type, right_type, for_assignment=False)
    # ^ unify_types might produce 'f64' if one side is f64, the other f32, etc.

    # 3) Insert a conversion node if needed for the left side
    if left_type != result_type:
        # Example: if left_type=f32, result_type=f64 => promote
        conv = ConversionExpression(
            source_expr=bin_expr.left,      # <--- keyword argument
            from_type=left_type,
            to_type=result_type
        )
        bin_expr.left = conv  # wrap left side

    # Similarly for the right side
    if right_type != result_type:
        conv = ConversionExpression(
            source_expr=bin_expr.right,     # <--- keyword argument
            from_type=right_type,
            to_type=result_type
        )
        bin_expr.right = conv

    # 4) Assign the final type to this binary expression
    bin_expr.inferred_type = result_type

    # return the final type
    return result_type


def check_fn_expression(fn_expr: FnExpression, symbol_table: dict) -> str:
    """
    Type-check a function call expression, e.g. sum(10, 20).

    Steps:
      1) Extract the function name (fn_expr.name) and look it up in 'symbol_table'.
      2) Check each argument's type against the declared param type.
      3) Return the function's declared return type (instead of hardcoding 'f64').
    """

    # 1) Get the function name
    #    fn_expr.name might be a VariableExpression, so do fn_expr.name.name
    fn_name = fn_expr.name.name

    # 2) Look up the function signature
    if fn_name not in symbol_table:
        raise TypeError(f"Undefined function '{fn_name}'")

    signature = symbol_table[fn_name]
    param_types = signature["param_types"]
    return_type = signature["return_type"]

    # 3) Check argument count
    if len(fn_expr.arguments) != len(param_types):
        raise TypeError(
            f"Function '{fn_name}' expects {len(param_types)} args, "
            f"but got {len(fn_expr.arguments)}."
        )

    # 4) For each argument, check the expression's type
    for i, arg in enumerate(fn_expr.arguments):
        arg_type = check_expression(arg, symbol_table)
        param_type = param_types[i]

        # If you have a unify or conversion logic, now's the time to apply it:
        # Possibly call unify_types(arg_type, param_type, for_assignment=True)
        # or insert a ConversionExpression if needed. Example:
        unified = unify_types(arg_type, param_type, for_assignment=True)
        if unified != param_type:
            raise TypeError(
                f"Argument {i+1} of '{fn_name}' mismatch: "
                f"expected '{param_type}', got '{arg_type}'."
            )

    # 5) The call's overall type is the function's declared return type
    fn_expr.inferred_type = return_type

    # Return it
    return return_type


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