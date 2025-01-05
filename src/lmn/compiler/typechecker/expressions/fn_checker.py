# file: lmn/compiler/typechecker/fn_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

class FnChecker(BaseExpressionChecker):
    def check(
        self,
        expr: FnExpression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Type-check a FnExpression (function call).

        1) Determine which scope to use (local_scope or symbol_table).
        2) Check if fn_name is in that scope => fn_info.
        3) If fn_info["is_closure"] is True => call _check_closure_call.
           Else if "required_params" in fn_info => builtin function => _check_builtin_function.
           Else => user-defined top-level => _check_user_function.
        """
        # 1) Decide which scope to use for lookups
        scope = local_scope if local_scope is not None else self.symbol_table

        # 2) get the function name
        fn_name = expr.name.name

        # if not found in the scope, raise
        if fn_name not in scope:
            raise TypeError(f"Undefined function '{fn_name}'")

        fn_info = scope[fn_name]

        # 3) Determine if it's a closure, a built-in, or a user-defined function
        if fn_info.get("is_closure"):
            return self._check_closure_call(expr, fn_info, scope)
        elif "required_params" in fn_info:
            return self._check_builtin_function(expr, fn_info, scope)
        else:
            return self._check_user_function(expr, fn_info, scope)

    def _check_closure_call(
        self,
        expr: FnExpression,
        fn_info: Dict[str, Any],
        scope: Dict[str, Any]
    ) -> str:
        """
        Type-check a call to a function stored in a variable (a 'closure').
        Example:  let sum_func = function(a, b) return a+b end
                  sum_func(3,4)
        We unify arguments with fn_info["param_names"] / ["param_types"] / ["return_type"].
        """
        param_names = fn_info.get("param_names", [])
        param_types = fn_info.get("param_types", [])
        return_type = fn_info.get("return_type", "void")

        # We'll re-use the logic similar to user-defined functions:
        final_args = [None] * len(param_names)
        next_positional_index = 0

        # 1) Parse arguments from expr.arguments
        for arg_node in expr.arguments:
            if isinstance(arg_node, AssignmentExpression):
                param_name = arg_node.left.name
                if param_name not in param_names:
                    raise TypeError(
                        f"Unknown parameter '{param_name}' in call to closure. "
                        f"Valid param names: {param_names}"
                    )
                idx = param_names.index(param_name)
                if final_args[idx] is not None:
                    raise TypeError(
                        f"Parameter '{param_name}' supplied more than once in closure call."
                    )
                final_args[idx] = arg_node.right
            else:
                # positional
                if next_positional_index >= len(param_names):
                    raise TypeError(
                        f"Too many arguments for closure. "
                        f"Expected {len(param_names)}, got more."
                    )
                final_args[next_positional_index] = arg_node
                next_positional_index += 1

        # 2) Check all required parameters have an argument
        for i, (p_name, p_type) in enumerate(zip(param_names, param_types)):
            if final_args[i] is None:
                raise TypeError(f"Missing required param '{p_name}' in closure call.")

        # 3) Type-check each argument & unify
        for i, arg_node in enumerate(final_args):
            arg_type = self.dispatcher.check_expression(arg_node, local_scope=scope)
            if param_types[i] is None:
                # If the closure param types were not known yet
                param_types[i] = arg_type
            else:
                # unify
                unified = unify_types(param_types[i], arg_type, for_assignment=True)
                if unified != param_types[i]:
                    raise TypeError(
                        f"Closure param '{param_names[i]}' expects '{param_types[i]}' "
                        f"but got '{arg_type}'"
                    )
            # store updated param type
            fn_info["param_types"][i] = param_types[i]

        # 4) Set the expression's inferred type
        expr.inferred_type = return_type
        return return_type

    def _check_builtin_function(
        self,
        expr: FnExpression,
        fn_info: dict,
        scope: Dict[str, Any]
    ) -> str:
        """
        Type-check a call to a built-in function (which has "required_params", "optional_params").
        """
        required_params = fn_info.get("required_params", {})
        optional_params = fn_info.get("optional_params", {})
        return_type = fn_info.get("return_type", "void")

        named_args = {}
        positional_args = []

        for arg in expr.arguments:
            if isinstance(arg, AssignmentExpression):
                param_name = arg.left.name
                param_type = self.dispatcher.check_expression(arg.right, local_scope=scope)
                named_args[param_name] = param_type
            else:
                arg_type = self.dispatcher.check_expression(arg, local_scope=scope)
                positional_args.append(arg_type)

        req_keys = list(required_params.keys())

        for i, pos_type in enumerate(positional_args):
            if i < len(req_keys):
                param_name = req_keys[i]
                unify_types(required_params[param_name], pos_type, for_assignment=True)
                named_args[param_name] = pos_type

        for req_name, req_type in required_params.items():
            if req_name not in named_args:
                raise TypeError(f"Missing required parameter '{req_name}' for builtin fn.")

        for opt_name, opt_type in optional_params.items():
            if opt_name in named_args:
                unify_types(opt_type, named_args[opt_name], for_assignment=True)

        expr.inferred_type = return_type
        return return_type

    def _check_user_function(
        self,
        expr: FnExpression,
        fn_info: dict,
        scope: Dict[str, Any]
    ) -> str:
        """
        Type-check a call to a user-defined top-level function (like function add(a,b)).
        """
        param_names = fn_info.get("param_names", [])
        param_types = fn_info.get("param_types", [])
        param_defaults = fn_info.get("param_defaults", [])
        return_type = fn_info.get("return_type", "void")

        num_params = len(param_names)
        if not (len(param_types) == len(param_defaults) == num_params):
            raise TypeError(
                f"Inconsistent function signature: param_names={num_params}, "
                f"param_types={len(param_types)}, param_defaults={len(param_defaults)}."
            )

        final_args = [None] * num_params
        next_positional_index = 0

        # 1) Parse arguments
        for arg_node in expr.arguments:
            if isinstance(arg_node, AssignmentExpression):
                param_name = arg_node.left.name
                if param_name not in param_names:
                    raise TypeError(
                        f"Unknown parameter '{param_name}' in call to '{expr.name.name}'. "
                        f"Valid names: {param_names}"
                    )
                idx = param_names.index(param_name)
                if final_args[idx] is not None:
                    raise TypeError(
                        f"Parameter '{param_name}' supplied more than once in call to '{expr.name.name}'."
                    )
                final_args[idx] = arg_node.right
            else:
                if next_positional_index >= num_params:
                    raise TypeError(
                        f"Too many arguments for '{expr.name.name}'. Expected {num_params}, got more."
                    )
                final_args[next_positional_index] = arg_node
                next_positional_index += 1

        # 2) Check missing required params / fill in defaults
        for i, (p_name, p_type, p_default) in enumerate(zip(param_names, param_types, param_defaults)):
            if final_args[i] is None:
                if p_default is None:
                    raise TypeError(
                        f"Missing required parameter '{p_name}' in call to '{expr.name.name}'."
                    )
                else:
                    final_args[i] = p_default

        # 3) Type-check each argument & unify
        for i, arg_node in enumerate(final_args):
            arg_type = self.dispatcher.check_expression(arg_node, local_scope=scope)
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

        expr.inferred_type = return_type
        return return_type
