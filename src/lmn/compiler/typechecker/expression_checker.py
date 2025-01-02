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
    if lit_expr.inferred_type is not None:
        return lit_expr.inferred_type

    # If parser gave literal_type == "f64", we set => "double"
    if lit_expr.literal_type == "f32":
        lit_expr.inferred_type = "float"
        return "float"
    elif lit_expr.literal_type == "f64":
        lit_expr.inferred_type = "double"
        return "double"

    if lit_expr.literal_type == "i32":
        lit_expr.inferred_type = "int"
        return "int"
    elif lit_expr.literal_type == "i64":
        lit_expr.inferred_type = "long"
        return "long"
    elif lit_expr.literal_type == "string":
        lit_expr.inferred_type = "string"
        return "string"

    # Otherwise => infer_literal_type(...)
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
    bin_expr.inferred_type = result_type

    # ------------------------------------------------------
    # Only build a ConversionExpression if both from_type and
    # to_type are valid strings (i.e., not None) and differ.
    # ------------------------------------------------------

    if left_type is not None and result_type is not None and left_type != result_type:
        bin_expr.left = ConversionExpression(
            source_expr=bin_expr.left,
            from_type=left_type,
            to_type=result_type
        )

    if right_type is not None and result_type is not None and right_type != result_type:
        bin_expr.right = ConversionExpression(
            source_expr=bin_expr.right,
            from_type=right_type,
            to_type=result_type
        )

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
    """
    Type checks a function call expression. Handles both positional and named arguments.
    """
    fn_name = fn_expr.name.name

    # 1) Ensure the function is known
    if fn_name not in symbol_table:
        raise TypeError(f"Undefined function '{fn_name}'")

    # 2) Get function signature info
    fn_info = symbol_table[fn_name]
    
    # Handle both builtin (with required/optional params) and user-defined functions
    if "required_params" in fn_info:
        # Builtin function case - uses named parameters
        return check_builtin_function_call(fn_expr, fn_info, symbol_table)
    else:
        # User-defined function case - uses positional parameters
        return check_user_function_call(fn_expr, fn_info, symbol_table)

def check_builtin_function_call(fn_expr: FnExpression, fn_info: dict, symbol_table: dict) -> str:
    """Handles builtin functions that use named parameters"""
    required_params = fn_info.get("required_params", {})
    optional_params = fn_info.get("optional_params", {})
    return_type = fn_info.get("return_type", "void")
    
    # Build dict of paramName => inferredType from arguments
    passed_args = {}
    
    for arg in fn_expr.arguments:
        if arg.type == "AssignmentExpression":
            param_name = arg.left.name
            param_type = check_expression(arg.right, symbol_table)
            passed_args[param_name] = param_type
        else:
            raise TypeError(
                f"Builtin function '{fn_expr.name.name}' must be called with named arguments like param=expr"
            )

    # Check required parameters
    for req_name, req_type in required_params.items():
        if req_name not in passed_args:
            raise TypeError(f"Missing required parameter '{req_name}' for builtin function '{fn_expr.name.name}'")
        
        actual_type = passed_args[req_name]
        unified = unify_types(req_type, actual_type, for_assignment=True)
        if unified != req_type:
            raise TypeError(
                f"Parameter '{req_name}' expects type '{req_type}' but got '{actual_type}'"
            )

    # Check optional parameters
    for opt_name, opt_type in optional_params.items():
        if opt_name in passed_args:
            actual_type = passed_args[opt_name]
            unified = unify_types(opt_type, actual_type, for_assignment=True)
            if unified != opt_type:
                raise TypeError(
                    f"Optional parameter '{opt_name}' expects type '{opt_type}' but got '{actual_type}'"
                )

    fn_expr.inferred_type = return_type
    return return_type

def check_user_function_call(fn_expr: FnExpression, fn_info: dict, symbol_table: dict) -> str:
    """
    Allows param inference if param_types[i] == None.
    """
    param_types = fn_info.get("param_types", [])
    return_type = fn_info.get("return_type", "void")  # might also be None initially

    # 1) Check argument count
    if len(fn_expr.arguments) != len(param_types):
        raise TypeError(
            f"Function '{fn_expr.name.name}' expects {len(param_types)} argument(s) "
            f"but got {len(fn_expr.arguments)}"
        )

    # 2) Type-check each argument
    for i, (arg_node, expected_type) in enumerate(zip(fn_expr.arguments, param_types)):
        arg_type = check_expression(arg_node, symbol_table)

        # If param_types[i] is None => set it to arg_type
        if expected_type is None:
            param_types[i] = arg_type
            fn_info["param_types"] = param_types
            expected_type = arg_type
        else:
            # unify
            unified = unify_types(expected_type, arg_type, for_assignment=True)
            if unified != expected_type:
                raise TypeError(
                    f"Argument {i+1} of function '{fn_expr.name.name}' "
                    f"expects type '{expected_type}' but got '{arg_type}'"
                )

    # 3) The call expression's result is the function's return type
    fn_expr.inferred_type = return_type
    return return_type


