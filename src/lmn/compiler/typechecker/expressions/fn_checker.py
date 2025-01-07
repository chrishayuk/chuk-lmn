# file: lmn/compiler/typechecker/expressions/fn_checker.py

from typing import Optional, Dict, Any

from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression

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

        We either see a user-defined function, a built-in function, or a closure in the scope.
        If the scope var is just "function", we patch it to a minimal dict
        so we can handle the call properly (instead of defaulting to 'void').
        """
        scope = local_scope if local_scope else self.symbol_table

        fn_name = expr.name.name
        if fn_name not in scope:
            raise TypeError(f"Undefined function '{fn_name}'")

        fn_info = scope[fn_name]

        # If 'fn_info' is just "function", convert it to a minimal closure dict
        if not isinstance(fn_info, dict):
            if fn_info == "function":
                fn_info = {
                    "is_closure": True,
                    "param_names": [],
                    "param_types": [],
                    "return_type": "void",
                }
                scope[fn_name] = fn_info
            else:
                raise TypeError(
                    f"Expected dict or 'function' for '{fn_name}', got {repr(fn_info)}"
                )

        # Decide: closure? builtin? or user-defined?
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
        Handle calls to a closure dictionary, e.g. add5(...).
        We unify each argument with the closure's param_types, then
        return the known closure return_type.
        """
        param_names = fn_info.get("param_names", [])
        param_types = fn_info.get("param_types", [])
        return_type = fn_info.get("return_type", "void")

        # If param_names are empty => define them from arg count
        if not param_names:
            param_count = len(expr.arguments)
            param_names = [f"_arg{i}" for i in range(param_count)]
            param_types = [None]*param_count
            fn_info["param_names"] = param_names
            fn_info["param_types"] = param_types

        final_args = [None] * len(param_names)
        next_positional_index = 0

        from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression

        # 1) Sort arguments
        for arg_node in expr.arguments:
            if isinstance(arg_node, AssignmentExpression):
                param_name = arg_node.left.name
                if param_name not in param_names:
                    raise TypeError(
                        f"Unknown parameter '{param_name}' in closure call to '{expr.name.name}'. "
                        f"Valid param names: {param_names}"
                    )
                idx = param_names.index(param_name)
                if final_args[idx] is not None:
                    raise TypeError(
                        f"Parameter '{param_name}' supplied more than once."
                    )
                final_args[idx] = arg_node.right
            else:
                if next_positional_index >= len(param_names):
                    raise TypeError(
                        f"Too many arguments for closure '{expr.name.name}'. "
                        f"Expected {len(param_names)}."
                    )
                final_args[next_positional_index] = arg_node
                next_positional_index += 1

        # 2) Check all required parameters have an argument
        for i, (p_name, p_type) in enumerate(zip(param_names, param_types)):
            if final_args[i] is None:
                raise TypeError(
                    f"Missing required param '{p_name}' in closure call."
                )

        # 3) Type-check each argument & unify
        for i, arg_node in enumerate(final_args):
            arg_type = self.dispatcher.check_expression(arg_node, local_scope=scope)
            if param_types[i] is None:
                param_types[i] = arg_type
            else:
                unified = unify_types(param_types[i], arg_type, for_assignment=True)
                if unified != param_types[i]:
                    raise TypeError(
                        f"Closure param '{param_names[i]}' expects '{param_types[i]}' "
                        f"but got '{arg_type}'"
                    )
            fn_info["param_types"][i] = param_types[i]

        # The closure's return_type is e.g. "int"
        expr.inferred_type = return_type
        return return_type

    def _check_builtin_function(
        self,
        expr: FnExpression,
        fn_info: Dict[str, Any],
        scope: Dict[str, Any]
    ) -> str:
        """
        Type-check a call to a built-in function with 'required_params', 'optional_params', etc.
        """
        required_params = fn_info.get("required_params", {})
        optional_params = fn_info.get("optional_params", {})
        return_type = fn_info.get("return_type", "void")

        from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression

        named_args = {}
        positional_args = []

        # 1) Collect named vs positional
        for arg in expr.arguments:
            if isinstance(arg, AssignmentExpression):
                param_name = arg.left.name
                param_type = self.dispatcher.check_expression(arg.right, local_scope=scope)
                named_args[param_name] = param_type
            else:
                arg_type = self.dispatcher.check_expression(arg, local_scope=scope)
                positional_args.append(arg_type)

        # 2) Unify positional with required params in order
        req_keys = list(required_params.keys())
        for i, pos_type in enumerate(positional_args):
            if i < len(req_keys):
                pname = req_keys[i]
                unify_types(required_params[pname], pos_type, for_assignment=True)
                named_args[pname] = pos_type

        # 3) Check required
        for req_name in required_params:
            if req_name not in named_args:
                raise TypeError(f"Missing required param '{req_name}' for builtin fn call.")

        # 4) Check optional
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
        Type-check a call to a user-defined top-level function.
        If return_type=="function", check if it returns an AnonymousFunction => produce a closure dict.
        """
        param_names = fn_info.get("param_names", [])
        param_types = fn_info.get("param_types", [])
        param_defaults = fn_info.get("param_defaults", [])
        return_type = fn_info.get("return_type", "void")

        num_params = len(param_names)
        if not (len(param_types) == len(param_defaults) == num_params):
            raise TypeError(
                f"Mismatch in user function signature: param_names={num_params}, "
                f"param_types={len(param_types)}, param_defaults={len(param_defaults)}."
            )

        final_args = [None] * num_params
        next_positional_index = 0

        from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression

        # 1) Sort arguments
        for arg_node in expr.arguments:
            if isinstance(arg_node, AssignmentExpression):
                pname = arg_node.left.name
                if pname not in param_names:
                    raise TypeError(
                        f"Unknown param '{pname}' in call to '{expr.name.name}'. Valid: {param_names}"
                    )
                idx = param_names.index(pname)
                if final_args[idx] is not None:
                    raise TypeError(f"Param '{pname}' repeated in call.")
                final_args[idx] = arg_node.right
            else:
                if next_positional_index >= num_params:
                    raise TypeError(
                        f"Too many arguments for '{expr.name.name}'. Expected {num_params}."
                    )
                final_args[next_positional_index] = arg_node
                next_positional_index += 1

        # 2) Check defaults
        for i, (pname, ptype, pdefault) in enumerate(zip(param_names, param_types, param_defaults)):
            if final_args[i] is None:
                if pdefault is None:
                    raise TypeError(
                        f"Missing required param '{pname}' in call to '{expr.name.name}'."
                    )
                final_args[i] = pdefault

        # 3) unify each argument
        for i, arg_node in enumerate(final_args):
            arg_type = self.dispatcher.check_expression(arg_node, local_scope=scope)
            if param_types[i] is None:
                param_types[i] = arg_type
            else:
                unified = unify_types(param_types[i], arg_type, for_assignment=True)
                if unified != param_types[i]:
                    raise TypeError(
                        f"Parameter '{param_names[i]}' expects '{param_types[i]}' got '{arg_type}'"
                    )
            fn_info["param_types"][i] = param_types[i]

        # 4) If return_type=="function", see if it returns an AnonymousFunction => produce a closure
        if return_type == "function":
            func_def_node = fn_info.get("ast_node", None)
            if func_def_node and len(func_def_node.body) > 0:
                last_stmt = func_def_node.body[-1]
                if last_stmt.type == "ReturnStatement":
                    maybe_anon = last_stmt.expression
                    if maybe_anon.type == "AnonymousFunction":
                        closure_params = maybe_anon.parameters   # e.g. [("y", "int")]
                        closure_param_names = [p[0] for p in closure_params]
                        closure_param_types = [p[1] for p in closure_params]
                        closure_return_type = maybe_anon.return_type or "void"

                        closure_info = {
                            "is_closure": True,
                            "param_names": closure_param_names,
                            "param_types": closure_param_types,
                            "return_type": closure_return_type
                        }
                        expr.inferred_type = closure_info
                        return closure_info

            # fallback
            expr.inferred_type = "function"
            return "function"

        # Otherwise => normal user function returning e.g. "int"
        expr.inferred_type = return_type
        return return_type
