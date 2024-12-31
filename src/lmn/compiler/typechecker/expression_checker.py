# file: lmn/compiler/typechecker/expression_checker.py

from typing import Optional

from lmn.compiler.ast import Expression

# Direct imports of expression classes
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression

# Utility or type-checker modules
from lmn.compiler.typechecker.utils import unify_types, infer_literal_type

def check_expression(expr: Expression, symbol_table: dict, target_type: Optional[str] = None) -> str:
    """
    Analyzes 'expr' and returns its final language-level type:
      - "int", "long", "float", "double", "json", "array", etc.

    - 'target_type' can hint how to interpret a literal (e.g., 10 -> "int" or "long").
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

    elif isinstance(expr, JsonLiteralExpression):
        return check_json_literal_expression(expr, symbol_table)

    elif isinstance(expr, ArrayLiteralExpression):
        return check_array_literal_expression(expr, symbol_table)

    else:
        raise NotImplementedError(f"Unsupported expression type: {expr.type}")


# -------------------------------------------------------------------------
# 1) JSON Literal
# -------------------------------------------------------------------------
def check_json_literal_expression(j_expr: JsonLiteralExpression, symbol_table: dict) -> str:
    """
    For now, treat any JSON literal (object/array) as having type 'json'.
    If you want more advanced logic (e.g. verifying fields or schema),
    you can recursively check j_expr.value (a Python dict/list).
    """
    j_expr.inferred_type = "json"
    return "json"


# -------------------------------------------------------------------------
# 2) Array Literal
# -------------------------------------------------------------------------
def check_array_literal_expression(arr_expr: ArrayLiteralExpression, symbol_table: dict) -> str:
    """
    If you want a strongly-typed array (e.g. all elements must unify),
    you can unify the type of each element. For example:
        - parse all element types
        - unify them (like numeric promotions)
        - final type might be "array of T" or just "array" if they differ
    For now, let's keep it simple: we call each element's type checker,
    but we won't unify them. We'll just mark the array as type "array".
    """
    element_types = []
    for elem in arr_expr.elements:
        elem_type = check_expression(elem, symbol_table)
        element_types.append(elem_type)

    # Option A (simple): just mark array as type 'array'
    arr_expr.inferred_type = "array"

    # Option B (unify all elements) -> 'array<T>' or something
    # e.g. if all elements unify to 'int', then 'array<int>'
    # For a minimal example:
    # final_elem_type = element_types[0] if element_types else "any"
    # for t in element_types[1:]:
    #     final_elem_type = unify_types(final_elem_type, t, for_assignment=False)
    # arr_expr.inferred_type = f"array<{final_elem_type}>"

    return arr_expr.inferred_type


# -------------------------------------------------------------------------
# 3) LiteralExpression
# -------------------------------------------------------------------------
def check_literal_expression(lit_expr: LiteralExpression, target_type: Optional[str] = None) -> str:
    """
    If a numeric literal is explicitly 'f32' or 'f64' (from parser),
    keep that. Otherwise, fall back to infer_literal_type.
    """
    if lit_expr.inferred_type is not None:
        # Already set by a previous step
        return lit_expr.inferred_type

    # --------------------------------
    # 1) If parser gave a literal_type
    # --------------------------------
    # e.g. "f32" => "float", "f64" => "double"
    if lit_expr.literal_type == "f32":
        lit_expr.inferred_type = "float"
        return "float"
    elif lit_expr.literal_type == "f64":
        lit_expr.inferred_type = "double"
        return "double"

    # If your parser sets "i32", "i64", or "string" in literal_type, handle those too:
    if lit_expr.literal_type == "i32":
        lit_expr.inferred_type = "int"
        return "int"
    elif lit_expr.literal_type == "i64":
        lit_expr.inferred_type = "long"
        return "long"
    elif lit_expr.literal_type == "string":
        lit_expr.inferred_type = "string"
        return "string"

    # --------------------------------
    # 2) If no parser-level literal_type
    #    => Fall back to existing inference
    # --------------------------------
    lit_expr.inferred_type = infer_literal_type(lit_expr.value, target_type)
    return lit_expr.inferred_type


# -------------------------------------------------------------------------
# 4) VariableExpression
# -------------------------------------------------------------------------
def check_variable_expression(var_expr: VariableExpression, symbol_table: dict) -> str:
    var_name = var_expr.name
    if var_name not in symbol_table:
        raise TypeError(f"Variable '{var_name}' used before assignment.")

    vtype = symbol_table[var_name]
    var_expr.inferred_type = vtype
    return vtype

# -------------------------------------------------------------------------
# 5) BinaryExpression
# -------------------------------------------------------------------------
def check_binary_expression(bin_expr: BinaryExpression, symbol_table: dict) -> str:
    left_type = check_expression(bin_expr.left, symbol_table)
    right_type = check_expression(bin_expr.right, symbol_table)

    # Non-assignment => pick the 'larger' type
    result_type = unify_types(left_type, right_type, for_assignment=False)

    # Insert ConversionExpression if mismatch
    if left_type != result_type:
        bin_expr.left = ConversionExpression(
            source_expr=bin_expr.left,
            from_type=left_type,
            to_type=result_type
        )

    if right_type != result_type:
        bin_expr.right = ConversionExpression(
            source_expr=bin_expr.right,
            from_type=right_type,
            to_type=result_type
        )

    bin_expr.inferred_type = result_type
    return result_type

# -------------------------------------------------------------------------
# 6) UnaryExpression
# -------------------------------------------------------------------------
def check_unary_expression(u_expr: UnaryExpression, symbol_table: dict) -> str:
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

# -------------------------------------------------------------------------
# 7) AssignmentExpression
# -------------------------------------------------------------------------
def check_assignment_expression(assign_expr: AssignmentExpression, symbol_table: dict) -> str:
    left_node = assign_expr.left
    right_node = assign_expr.right

    if not isinstance(left_node, VariableExpression):
        raise TypeError(f"Assignment LHS must be a variable, got '{left_node.type}'")

    var_name = left_node.name
    right_type = check_expression(right_node, symbol_table)

    if var_name in symbol_table:
        existing_type = symbol_table[var_name]
        # unify with for_assignment=True => allows int->float promotions
        unified = unify_types(existing_type, right_type, for_assignment=True)

        symbol_table[var_name] = unified
        assign_expr.inferred_type = unified
    else:
        # Declare on the fly
        symbol_table[var_name] = right_type
        assign_expr.inferred_type = right_type

    return assign_expr.inferred_type

# -------------------------------------------------------------------------
# 8) PostfixExpression
# -------------------------------------------------------------------------
def check_postfix_expression(p_expr: PostfixExpression, symbol_table: dict) -> str:
    operand_type = check_expression(p_expr.operand, symbol_table)
    operator = p_expr.operator  # '++' or '--'

    if operand_type not in ("int", "long", "float", "double"):
        raise TypeError(f"Cannot apply postfix '{operator}' to '{operand_type}'. Must be numeric.")

    p_expr.inferred_type = operand_type
    return operand_type

# -------------------------------------------------------------------------
# 9) FnExpression
# -------------------------------------------------------------------------
def check_fn_expression(fn_expr: FnExpression, symbol_table: dict) -> str:
    fn_name = fn_expr.name.name
    if fn_name not in symbol_table:
        raise TypeError(f"Undefined function '{fn_name}'")

    fn_sig = symbol_table[fn_name]  # e.g. {"param_types":["int","int"], "return_type":"float"}
    param_types = fn_sig["param_types"]
    return_type = fn_sig["return_type"]

    if len(fn_expr.arguments) != len(param_types):
        raise TypeError(f"Function '{fn_name}' expects {len(param_types)} args, "
                        f"but got {len(fn_expr.arguments)}.")

    for i, arg in enumerate(fn_expr.arguments):
        arg_type = check_expression(arg, symbol_table)
        old_param_type = param_types[i]

        # for_assignment=True => allows numeric promotions
        new_param_type = unify_types(old_param_type, arg_type, for_assignment=True)
        param_types[i] = new_param_type

    fn_expr.inferred_type = return_type
    return return_type
