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
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression

# Typechecker utilities (using "int", "long", "float", "double")
from lmn.compiler.typechecker.utils import unify_types, infer_literal_type


def check_expression(expr: Expression, symbol_table: dict, target_type: Optional[str] = None) -> str:
    """
    Analyzes 'expr' and returns its final language-level type:
    - "int", "long", "float", "double", etc.

    - 'target_type' can hint how to interpret a literal (e.g. 10 -> "int" or "long").
    - 'symbol_table' contains known variable/function definitions.

    The expression's final type is stored in 'expr.inferred_type' as well.
    """

    if isinstance(expr, LiteralExpression):
        return check_literal_expression(expr, target_type)

    elif isinstance(expr, VariableExpression):
        return check_variable_expression(expr, symbol_table)

    elif isinstance(expr, BinaryExpression):
        return check_binary_expression(expr, symbol_table)

    elif isinstance(expr, UnaryExpression):
        return check_unary_expression(expr, symbol_table)

    elif isinstance(expr, AssignmentExpression):
        return check_assignment_expression(expr, symbol_table)

    elif isinstance(expr, PostfixExpression):
        return check_postfix_expression(expr, symbol_table)

    elif isinstance(expr, FnExpression):
        return check_fn_expression(expr, symbol_table)

    else:
        raise NotImplementedError(f"Unsupported expression type: {expr.type}")


def check_binary_expression(bin_expr: BinaryExpression, symbol_table: dict) -> str:
    """
    1) Type-check left and right sub-expressions.
    2) Use 'unify_types(..., for_assignment=False)' to pick the 'larger' type (e.g. int+float => float).
    3) If sub-expr type != unified type, wrap in a ConversionExpression.
    4) Store final type in bin_expr.inferred_type.
    """

    left_type = check_expression(bin_expr.left, symbol_table)
    right_type = check_expression(bin_expr.right, symbol_table)

    # Non-assignment => pick the larger type
    result_type = unify_types(left_type, right_type, for_assignment=False)

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

    bin_expr.inferred_type = result_type
    return result_type


def check_postfix_expression(p_expr: PostfixExpression, symbol_table: dict) -> str:
    """
    e.g. a++, b-- => operand must be numeric. 
    The result is the same type as the operand, like C/C++ semantics.
    """

    operand_type = check_expression(p_expr.operand, symbol_table)
    operator = p_expr.operator  # '++' or '--'

    if operand_type not in ("int", "long", "float", "double"):
        raise TypeError(f"Cannot apply postfix '{operator}' to '{operand_type}'. Must be numeric.")

    p_expr.inferred_type = operand_type
    return operand_type


def check_fn_expression(fn_expr: FnExpression, symbol_table: dict) -> str:
    """
    Type-check a function call:
      1) Symbol table must have {fn_name: { "param_types": [...], "return_type": ... }}
      2) Arg count must match param_types length.
      3) We unify param_type with arg_type (for_assignment=True). If it returns a "larger" type,
         we update the function's param_type to reflect that promotion (e.g. int -> double).
      4) The call's own type is the function's declared return type.
    """

    fn_name = fn_expr.name.name
    if fn_name not in symbol_table:
        raise TypeError(f"Undefined function '{fn_name}'")

    fn_sig = symbol_table[fn_name]  # e.g. { "param_types":["int","int"], "return_type":"float" }
    param_types = fn_sig["param_types"]
    return_type = fn_sig["return_type"]

    if len(fn_expr.arguments) != len(param_types):
        raise TypeError(f"Function '{fn_name}' expects {len(param_types)} args, "
                        f"but got {len(fn_expr.arguments)}.")

    for i, arg in enumerate(fn_expr.arguments):
        arg_type = check_expression(arg, symbol_table)
        old_param_type = param_types[i]

        # "for_assignment=True" => we unify old_param_type with arg_type,
        # allowing promotion from e.g. int -> double
        new_param_type = unify_types(old_param_type, arg_type, for_assignment=True)

        # If unification fails, unify_types(...) will raise TypeError
        # If it succeeds but differs (promotion), we update param_types[i].
        param_types[i] = new_param_type

    # The call’s own type is the function’s declared return type
    fn_expr.inferred_type = return_type
    return return_type



def check_literal_expression(lit_expr: LiteralExpression, target_type: Optional[str] = None) -> str:
    """
    If a numeric literal: e.g. int => "int", float => "double" by default (unless target_type is "float").
    If string => "string". Possibly others if you extend the language.
    """

    if lit_expr.inferred_type is not None:
        return lit_expr.inferred_type

    lit_expr.inferred_type = infer_literal_type(lit_expr.value, target_type)
    return lit_expr.inferred_type


def check_unary_expression(u_expr: UnaryExpression, symbol_table: dict) -> str:
    """
    e.g. +, - for numeric, or 'not' for boolean if your language uses int as boole.
    """

    operand_type = check_expression(u_expr.operand, symbol_table)
    op = u_expr.operator

    if op in ("+", "-"):
        if operand_type not in ("int", "long", "float", "double"):
            raise TypeError(f"Cannot apply unary '{op}' to '{operand_type}'. Must be numeric.")
        result_type = operand_type

    elif op == "not":
        if operand_type != "int":
            raise TypeError(f"Cannot apply 'not' to '{operand_type}'. Expecting 'int' as boolean.")
        result_type = "int"

    else:
        raise NotImplementedError(f"Unknown unary operator '{op}'")

    u_expr.inferred_type = result_type
    return result_type


def check_variable_expression(var_expr: VariableExpression, symbol_table: dict) -> str:
    """
    Looks up var_expr.name in the symbol table. If not found => error.
    Otherwise sets var_expr.inferred_type to that type.
    """

    var_name = var_expr.name
    if var_name not in symbol_table:
        raise TypeError(f"Variable '{var_name}' used before assignment.")

    vtype = symbol_table[var_name]
    var_expr.inferred_type = vtype
    return vtype


def check_assignment_expression(assign_expr: AssignmentExpression, symbol_table: dict) -> str:
    """
    e.g. a = expr or a += expr => parser transforms it to 'a = a + expr'.
    Steps:
      1) left must be VariableExpression
      2) type-check the right side
      3) unify for_assignment=True => if var was int but expr is float => var->float if allowed
      4) store final type in symbol_table[var_name]
      5) assign_expr.inferred_type = final type
    """

    left_node = assign_expr.left
    right_node = assign_expr.right

    if not isinstance(left_node, VariableExpression):
        raise TypeError(f"Assignment LHS must be a variable, got '{left_node.type}'")

    var_name = left_node.name
    right_type = check_expression(right_node, symbol_table)

    if var_name in symbol_table:
        existing_type = symbol_table[var_name]
        unified = unify_types(existing_type, right_type, for_assignment=True)

        # If e.g. int->float, we do 'symbol_table[var_name] = float'
        symbol_table[var_name] = unified
        assign_expr.inferred_type = unified

    else:
        # variable not in symbol_table => declare on the fly
        symbol_table[var_name] = right_type
        assign_expr.inferred_type = right_type

    return assign_expr.inferred_type
