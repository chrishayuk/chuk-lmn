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

# Direct imports of expression classes (to avoid mega_union issues)
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression

# Typechecker utilities (revised to use "int", "long", "float", "double")
from lmn.compiler.typechecker.utils import unify_types, infer_literal_type


def check_expression(expr: Expression, symbol_table: dict, target_type: Optional[str] = None) -> str:
    """
    Analyzes an expression and returns its final (language-level) type:
      "int", "long", "float", or "double" (or other types as your language grows).

    The inferred type is also stored in `expr.inferred_type`.
    If you supply a `target_type`, it can guide literal inference (e.g. 10 → "int").
    """

    if isinstance(expr, LiteralExpression):
        return check_literal_expression(expr, target_type)
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


def check_binary_expression(bin_expr: BinaryExpression, symbol_table: dict) -> str:
    """
    Type-check left and right sub-expressions, unify their types, and update `bin_expr`.
    If a sub-expression needs to be promoted (e.g., "int" -> "long"), we insert a
    `ConversionExpression` node around that side.
    """

    # 1) Resolve types for left and right
    left_type = check_expression(bin_expr.left, symbol_table)
    right_type = check_expression(bin_expr.right, symbol_table)

    # 2) Determine the unified result type
    result_type = unify_types(left_type, right_type, for_assignment=False)

    # 3) If either side’s type differs from the unified type, wrap in a ConversionExpression
    if left_type != result_type:
        conv = ConversionExpression(
            source_expr=bin_expr.left,
            from_type=left_type,
            to_type=result_type
        )
        bin_expr.left = conv

    if right_type != result_type:
        conv = ConversionExpression(
            source_expr=bin_expr.right,
            from_type=right_type,
            to_type=result_type
        )
        bin_expr.right = conv

    # 4) Assign the final type
    bin_expr.inferred_type = result_type
    return result_type


def check_fn_expression(fn_expr: FnExpression, symbol_table: dict) -> str:
    """
    Type-checks a function call like sum(10, 20):
      1) Looks up the function signature in `symbol_table`.
      2) Ensures argument count matches.
      3) Checks each argument’s type vs. the declared parameter type.
      4) The call’s type is the function’s declared return type.
    """

    # 1) Get the function name (from a VariableExpression stored in fn_expr.name)
    fn_name = fn_expr.name.name

    # 2) Retrieve the function’s signature from the symbol table
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

    # 4) For each argument, check the type and unify with param_type
    for i, arg in enumerate(fn_expr.arguments):
        arg_type = check_expression(arg, symbol_table)  # no target_type here
        param_type = param_types[i]

        unified = unify_types(arg_type, param_type, for_assignment=True)
        if unified != param_type:
            raise TypeError(
                f"Argument {i+1} of '{fn_name}' mismatch: "
                f"expected '{param_type}', got '{arg_type}'."
            )

    # 5) The function call’s overall type is the function’s declared return type
    fn_expr.inferred_type = return_type
    return return_type


def check_literal_expression(lit_expr: LiteralExpression, target_type: Optional[str] = None) -> str:
    """
    Infers the type of a numeric or string literal based on `target_type`
    (e.g., if target_type="float" and the literal is numeric, pick "float").
    """

    # If already determined, just return it
    if lit_expr.inferred_type is not None:
        return lit_expr.inferred_type

    # Otherwise, infer from the literal value
    lit_expr.inferred_type = infer_literal_type(lit_expr.value, target_type)
    return lit_expr.inferred_type


def check_unary_expression(u_expr: UnaryExpression, symbol_table: dict) -> str:
    """
    Examples of unary operators in many languages:
      + <expr>
      - <expr>
      not <expr>

    Adjust the logic as needed for your language’s semantics.
    """

    operand_type = check_expression(u_expr.operand, symbol_table)
    op = u_expr.operator

    # Unary plus doesn't change the operand's type
    if op == "+":
        # Must be a numeric type if your language enforces that
        if operand_type not in ("int", "long", "float", "double"):
            raise TypeError(f"Cannot apply unary '+' to type {operand_type}")
        result_type = operand_type

    elif op == "-":
        # Must be a numeric type
        if operand_type not in ("int", "long", "float", "double"):
            raise TypeError(f"Cannot apply unary '-' to type {operand_type}")
        result_type = operand_type

    elif op == "not":
        # If your language treats `not` as boolean, and `int` means boolean-ish,
        # then ensure the operand is "int". Otherwise, adjust to "bool" if you have that.
        if operand_type != "int":
            raise TypeError(f"'not' operator requires 'int' operand, got '{operand_type}'")
        # The result is also "int" (or "bool", if that’s your language’s boolean type).
        result_type = "int"

    else:
        raise NotImplementedError(f"Unknown unary operator '{op}'")

    u_expr.inferred_type = result_type
    return result_type


def check_variable_expression(var_expr: VariableExpression, symbol_table: dict) -> str:
    """
    Retrieves the variable’s declared/inferred type from `symbol_table`.
    Raises an error if it's not defined.
    """

    var_name = var_expr.name
    if var_name not in symbol_table:
        raise TypeError(f"Variable '{var_name}' used before assignment.")

    vtype = symbol_table[var_name]
    var_expr.inferred_type = vtype
    return vtype
