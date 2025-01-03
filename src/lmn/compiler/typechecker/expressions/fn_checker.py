
# file: lmn/compiler/typechecker/fn_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

# -------------------------------------------------------------------------
# 9) FnExpression
# -------------------------------------------------------------------------

class FnChecker(BaseExpressionChecker):
    def check(self, expr: FnExpression, target_type: Optional[str] = None) -> str:
        # get the function name
        fn_name = expr.name.name

        # check the function name is in the symbol table
        if fn_name not in self.symbol_table:
            # raise an error
            raise TypeError(f"Undefined function '{fn_name}'")
        
        # get the function info
        fn_info = self.symbol_table[fn_name]

        # check the function is a builtin function
        if "required_params" in fn_info:
            # check the built in function
            return self._check_builtin_function(expr, fn_info)
        else:
            # check the user function
            return self._check_user_function(expr, fn_info)

    def _check_builtin_function(self, expr: FnExpression, fn_info: dict) -> str:
        # get required and optional parameters
        required_params = fn_info.get("required_params", {})
        optional_params = fn_info.get("optional_params", {})

        # get the return type
        return_type = fn_info.get("return_type", "void")

        # get the arguments
        named_args = {}
        positional_args = []

        # loop through each argument
        for arg in expr.arguments:
            # if the argument is a named argument
            if isinstance(arg, AssignmentExpression):
                # get the parameter name and type
                param_name = arg.left.name
                param_type = self.dispatcher.check_expression(arg.right)

                # check the parameter name is valid
                named_args[param_name] = param_type
            else:
                # get the argument type
                arg_type = self.dispatcher.check_expression(arg)

                # check the argument type is valid
                positional_args.append(arg_type)

        # check the number of arguments is correct
        req_keys = list(required_params.keys())

        # check the positional arguments
        for i, pos_type in enumerate(positional_args):
            # check the length of the positional arguments is correct
            if i < len(req_keys):
                # get the parameter name and type
                param_name = req_keys[i]

                # unify the types
                unify_types(required_params[param_name], pos_type, for_assignment=True)

                # add the parameter to the named arguments
                named_args[param_name] = pos_type

        # loop through the required parameters and check if they are in the named arguments
        for req_name, req_type in required_params.items():
            # check if the parameter is in the named arguments
            if req_name not in named_args:
                # raise an error
                raise TypeError(f"Missing required parameter '{req_name}'")
            
        # loop through optional parameters and check if they are in the named arguments
        for opt_name, opt_type in optional_params.items():
            # check if the parameter is in the named arguments
            if opt_name in named_args:
                # unify the types
                unify_types(opt_type, named_args[opt_name], for_assignment=True)

        # set the inferred type of the expression as the return type of the function
        expr.inferred_type = return_type

        # return the inferred type of the expressions
        return return_type

    def _check_user_function(self, expr: FnExpression, fn_info: dict) -> str:
        # get the parameter names and types
        param_names = fn_info.get("param_names", [])
        param_types = fn_info.get("param_types", [])
        param_defaults = fn_info.get("param_defaults", [])
        return_type = fn_info.get("return_type", "void")

        # check the number of parameters
        num_params = len(param_names)

        # check the number of arguments
        if not (len(param_types) == len(param_defaults) == num_params):
            raise TypeError(
                f"Inconsistent function signature for '{expr.name.name}': "
                f"param_names={num_params}, param_types={len(param_types)}, param_defaults={len(param_defaults)}."
            )
        
        # check the types of arguments
        final_args = [None] * num_params
        next_positional_index = 0

        # check named arguments first
        for arg_node in expr.arguments:
            # if the argument node is an assignment expression, it's a named parameter
            if isinstance(arg_node, AssignmentExpression):
                # get the parameter name and value
                param_name = arg_node.left.name

                # check that the parameter name is valid
                if param_name not in param_names:
                    # raise an error if the parameter name is not valid
                    raise TypeError(
                        f"Unknown parameter '{param_name}' in call to '{expr.name.name}'. "
                        f"Valid names: {param_names}"
                    )
                
                # check that the parameter has not already been supplied
                idx = param_names.index(param_name)

                # check that the parameter has not already been supplied
                if final_args[idx] is not None:
                    # raise an error if the parameter has already been supplied
                    raise TypeError(
                        f"Parameter '{param_name}' supplied more than once in call to '{expr.name.name}'."
                    )
                
                # set the argument value
                final_args[idx] = arg_node.right
            else:
                # check we have correct number of arguments
                if next_positional_index >= num_params:
                    # raise an error if there are too many arguments
                    raise TypeError(
                        f"Too many arguments for '{expr.name.name}'. "
                        f"Expected {num_params}, got more."
                    )
                
                # set the argument value
                final_args[next_positional_index] = arg_node

                # increment the positional index
                next_positional_index += 1

        # check that all required arguments have been supplied
        for i, (p_name, p_type, p_default) in enumerate(zip(param_names, param_types, param_defaults)):
            # if the argument has not been supplied
            if final_args[i] is None:
                # if the parameter has a default value
                if p_default is None:
                    # raise an error
                    raise TypeError(
                        f"Missing required parameter '{p_name}' in call to '{expr.name.name}'."
                    )
                else:
                    # set the argument to the default value
                    final_args[i] = p_default

        # check that all arguments are of the correct type
        for i, arg_node in enumerate(final_args):
            # check that the argument is of the correct type
            arg_type = self.dispatcher.check_expression(arg_node)
            
            # check there is a parameter at this index
            if param_types[i] is None:
                # if there is not, add the argument to the parameter types
                param_types[i] = arg_type
            else:
                # unify the types of the parameter and argument
                unified = unify_types(param_types[i], arg_type, for_assignment=True)
                
                # check that the unified type is not None
                if unified != param_types[i]:
                    raise TypeError(
                        f"Parameter '{param_names[i]}' expects type '{param_types[i]}' "
                        f"but got '{arg_type}'"
                    )
                
            # set the argument to the unified type
            fn_info["param_types"][i] = param_types[i]

        # set the return type of the function
        expr.inferred_type = return_type

        # return the inferred type of the function
        return return_type

