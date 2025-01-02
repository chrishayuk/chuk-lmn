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
      - "int", "long", "float", "double", "json", "string", etc.

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
    j_expr.inferred_type = "json"
    return "json"


# -------------------------------------------------------------------------
# 2) Array Literal
# -------------------------------------------------------------------------
def check_array_literal_expression(arr_expr: ArrayLiteralExpression, symbol_table: dict) -> str:
    for elem in arr_expr.elements:
        check_expression(elem, symbol_table)

    # For simplicity, we say it's just "array".
    arr_expr.inferred_type = "array"
    return "array"


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

    result_type = unify_types(left_type, right_type, for_assignment=False)
    bin_expr.inferred_type = result_type

    # If necessary, insert ConversionExpressions
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

    if "required_params" in fn_info:
        # Builtin function case - uses named parameters
        return check_builtin_function_call(fn_expr, fn_info, symbol_table)
    else:
        # User-defined function case - uses param_names/param_types/param_defaults
        return check_user_function_call(fn_expr, fn_info, symbol_table)


def check_builtin_function_call(fn_expr: FnExpression, fn_info: dict, symbol_table: dict) -> str:
    required_params = fn_info.get("required_params", {})
    optional_params = fn_info.get("optional_params", {})
    return_type     = fn_info.get("return_type", "void")

    # 1) Collect named arguments
    named_args = {}
    positional_args = []
    for arg in fn_expr.arguments:
        if arg.type == "AssignmentExpression":
            param_name = arg.left.name
            param_type = check_expression(arg.right, symbol_table)
            named_args[param_name] = param_type
        else:
            # It's a positional argument
            arg_type = check_expression(arg, symbol_table)
            positional_args.append(arg_type)
    
    # 2) If you want to treat positional arguments as filling required params in order
    req_keys = list(required_params.keys())
    opt_keys = list(optional_params.keys())
    i = 0
    # fill required first
    for pos_type in positional_args:
        if i < len(req_keys):
            param_name = req_keys[i]
            # unify types with required_params[param_name]
            unify_types(required_params[param_name], pos_type, for_assignment=True)
            # Mark that as "satisfied"
            named_args[param_name] = pos_type
        else:
            # maybe fill optional_params next, or raise if you have none left
            pass
        i += 1

    # 3) Now verify required params are all present
    for req_name, req_type in required_params.items():
        if req_name not in named_args:
            raise TypeError(...)

    # 4) Check optional params
    for opt_name, opt_type in optional_params.items():
        if opt_name in named_args:
            unify_types(opt_type, named_args[opt_name], for_assignment=True)
        # else it's not provided => that's okay

    fn_expr.inferred_type = return_type
    return return_type



def check_user_function_call(fn_expr: FnExpression, fn_info: dict, symbol_table: dict) -> str:
    """
    Extended version to handle named args + optional params in user-defined functions.
    
    We assume fn_info includes:
       fn_info["param_names"] = ["a", "b", ...]
       fn_info["param_types"] = [None or "int" or "string", ...]
       fn_info["param_defaults"] = [None or some default literal node, ...]
         (If param_defaults[i] != None, param i is "optional".)
    """
    param_names = fn_info.get("param_names", [])
    param_types = fn_info.get("param_types", [])
    param_defaults = fn_info.get("param_defaults", [])
    return_type = fn_info.get("return_type", "void")

    num_params = len(param_names)
    # Ensure arrays align
    if not (len(param_types) == len(param_defaults) == num_params):
        raise TypeError(
            f"Inconsistent function signature for '{fn_expr.name.name}': "
            f"param_names={num_params}, param_types={len(param_types)}, param_defaults={len(param_defaults)}."
        )

    # Build an array to hold final AST nodes for each param
    final_args = [None] * num_params
    next_positional_index = 0

    # Distribute arguments
    for arg_node in fn_expr.arguments:
        if arg_node.type == "AssignmentExpression":
            param_name = arg_node.left.name
            if param_name not in param_names:
                raise TypeError(
                    f"Unknown parameter '{param_name}' in call to '{fn_expr.name.name}'. "
                    f"Valid names: {param_names}"
                )
            idx = param_names.index(param_name)
            if final_args[idx] is not None:
                raise TypeError(
                    f"Parameter '{param_name}' supplied more than once in call to '{fn_expr.name.name}'."
                )
            final_args[idx] = arg_node.right
        else:
            # Positional argument
            if next_positional_index >= num_params:
                raise TypeError(
                    f"Too many arguments for '{fn_expr.name.name}'. "
                    f"Expected {num_params}, got more."
                )
            final_args[next_positional_index] = arg_node
            next_positional_index += 1

    # Fill in defaults or raise error if missing
    for i, (p_name, p_type, p_default) in enumerate(zip(param_names, param_types, param_defaults)):
        if final_args[i] is None:
            if p_default is None:
                raise TypeError(
                    f"Missing required parameter '{p_name}' in call to '{fn_expr.name.name}'."
                )
            else:
                final_args[i] = p_default

    # Type-check each final argument
    for i, arg_node in enumerate(final_args):
        arg_type = check_expression(arg_node, symbol_table)
        if param_types[i] is None:
            param_types[i] = arg_type
        else:
            unified = unify_types(param_types[i], arg_type, for_assignment=True)
            if unified != param_types[i]:
                raise TypeError(
                    f"Parameter '{param_names[i]}' expects type '{param_types[i]}' "
                    f"but got '{arg_type}'"
                )
        fn_info["param_types"][i] = param_types[i]

    # The call expression's result is the function's return type
    fn_expr.inferred_type = return_type
    return return_type
