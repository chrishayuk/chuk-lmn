# file: lmn/compiler/typechecker/statements/let_statement_checker.py
import logging
from typing import Dict

# AST imports
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression

# Base checker and utils
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import normalize_type, unify_types

logger = logging.getLogger(__name__)

class LetStatementChecker(BaseStatementChecker):
    """
    A subclass of BaseStatementChecker to handle type checking
    for 'let' statements.

    It covers:
      1) Normal array / JSON / literal assignment
      2) Anonymous function (closure) assignment
      3) Aliasing an existing function or closure (e.g. 'let sum_func_alias = add')
    """

    def check(self, stmt, local_scope: Dict[str, str] = None) -> None:
        """
        Type-check a 'let' statement and update either the local_scope or
        the global symbol table. If the right-hand side is an anonymous
        function, store it (and type-check its body). If it's an existing 
        function reference (alias), copy its signature. Otherwise, unify 
        with declared or inferred types.
        """
        # Decide which table to modify
        scope = local_scope if local_scope is not None else self.symbol_table

        var_name = stmt.variable.name
        logger.debug(f"Processing 'let' statement for variable '{var_name}'")

        # Possibly "int", "string[]", etc. Could be None if no annotation.
        type_annotation = getattr(stmt, "type_annotation", None)
        declared_type = normalize_type(type_annotation) if type_annotation else None
        logger.debug(f"Type annotation for '{var_name}': {declared_type}")

        # The right-hand side expression
        expr = stmt.expression

        # A) No expression => must have annotation or raise error
        if not expr:
            logger.debug(f"No initializer expression for 'let {var_name}'.")
            if not declared_type:
                raise TypeError(
                    f"No type annotation or initializer for '{var_name}' in let statement."
                )
            # Mark variable in scope with declared type
            scope[var_name] = declared_type
            stmt.variable.inferred_type = declared_type
            stmt.inferred_type = declared_type
            self._mark_assigned(scope, var_name)
            logger.debug(f"Marking '{var_name}' as '{declared_type}' in scope.")
            return

        # B) Check if the expression is an AnonymousFunction
        if isinstance(expr, AnonymousFunctionExpression):
            logger.debug(f"Detected an inline anonymous function for variable '{var_name}'")

            # Gather param names/types
            param_names = []
            param_types = []
            for (p_name, p_type) in expr.parameters:
                param_names.append(p_name)
                # If p_type is missing, default to 'int' or a suitable fallback
                param_types.append(p_type or "int")

            # 1) Create a new local scope for the function
            function_scope = dict(scope)
            function_scope["__current_function_return_type__"] = expr.return_type or "void"
            assigned_vars = function_scope.get("__assigned_vars__", set())

            # Insert parameters into function scope
            for i, p_name in enumerate(param_names):
                function_scope[p_name] = param_types[i]
                assigned_vars.add(p_name)
            function_scope["__assigned_vars__"] = assigned_vars

            # 2) Type-check each statement in expr.body
            for stmt_in_body in expr.body:
                self.dispatcher.check_statement(stmt_in_body, local_scope=function_scope)

            # 3) Get the final return type from the function scope
            final_return_type = function_scope.get("__current_function_return_type__", "void")
            expr.return_type = final_return_type  # store on the node
            expr.inferred_type = "function"

            # 4) Optionally store closure info in the scope
            closure_info = {
                "is_closure": True,
                "param_names": param_names,
                "param_types": param_types,
                "return_type": final_return_type,
                "ast_node": expr
            }
            scope[var_name] = closure_info

            # Mark the let-stmt and var node as "function"
            stmt.inferred_type = "function"
            stmt.variable.inferred_type = "function"
            self._mark_assigned(scope, var_name)
            return

        # C) Check if the expression is a VariableExpression referencing a known function/closure
        #    e.g. let sum_func_alias = add
        if isinstance(expr, VariableExpression):
            rhs_name = expr.name
            # If the RHS is in scope and is a function or closure => alias
            if rhs_name in scope:
                rhs_info = scope[rhs_name]
                if rhs_info.get("is_closure") or rhs_info.get("is_function") or "param_names" in rhs_info:
                    logger.debug(
                        f"Aliasing function '{rhs_name}' to new variable '{var_name}'"
                    )
                    # Copy param signature arrays
                    param_names = rhs_info.get("param_names", [])
                    param_types = rhs_info.get("param_types", [])
                    param_defaults = rhs_info.get("param_defaults", [])
                    return_type = rhs_info.get("return_type", None)

                    alias_info = {
                        "is_function": True,
                        "param_names": param_names,
                        "param_types": param_types,
                        "param_defaults": param_defaults,
                        "return_type": return_type,
                    }

                    final_type = "function"
                    scope[var_name] = alias_info
                    stmt.inferred_type = final_type
                    stmt.variable.inferred_type = final_type
                    expr.inferred_type = final_type
                    self._mark_assigned(scope, var_name)
                    return
                else:
                    # The RHS is a variable but not a function => unify as normal
                    logger.debug(f"RHS '{rhs_name}' not recognized as function/closure; continuing normal flow...")

        # D) Otherwise => do array/JSON/unification logic as normal
        logger.debug(f"Type-checking expression for variable '{var_name}'.")
        expr_type = self.dispatcher.check_expression(
            expr, target_type=declared_type, local_scope=scope
        )
        logger.debug(f"Expression type for '{var_name}' => {expr_type}")

        if declared_type:
            # 1) If declared_type ends with "[]", handle typed arrays
            if declared_type.endswith("[]"):
                base_type = declared_type[:-2]  # e.g. "int[]" => "int"
                if expr_type == "array":
                    all_ok = True
                    if hasattr(expr, "elements"):
                        for element_expr in getattr(expr, "elements", []):
                            elem_type = getattr(element_expr, "inferred_type", None)
                            if not elem_type:
                                elem_type = self.dispatcher.check_expression(element_expr, local_scope=scope)
                            unified = unify_types(base_type, elem_type, for_assignment=True)
                            if unified != base_type:
                                all_ok = False
                                break
                    else:
                        all_ok = False

                    if not all_ok:
                        raise TypeError(
                            f"Array elements do not match '{base_type}' for var '{var_name}'"
                        )

                    scope[var_name] = declared_type
                    stmt.inferred_type = declared_type
                    stmt.variable.inferred_type = declared_type
                    expr.inferred_type = declared_type
                    self._mark_assigned(scope, var_name)
                    return

                elif expr_type == "json":
                    # Possibly a JSON-literal array => check each element
                    if expr.type == "JsonLiteralExpression" and isinstance(expr.value, list):
                        all_ok = True
                        for val in expr.value:
                            if base_type == "int":
                                if not isinstance(val, int):
                                    all_ok = False
                                    break
                            elif base_type == "long":
                                if not isinstance(val, int):
                                    all_ok = False
                                    break
                            elif base_type in {"float", "double"}:
                                if not (isinstance(val, float) or isinstance(val, int)):
                                    all_ok = False
                                    break
                            elif base_type == "string":
                                if not isinstance(val, str):
                                    all_ok = False
                                    break
                            elif base_type == "json":
                                if not (isinstance(val, dict) or isinstance(val, list)):
                                    all_ok = False
                                    break
                            else:
                                raise TypeError(
                                    f"Unsupported base type '{base_type}' in let statement."
                                )

                        if not all_ok:
                            raise TypeError(
                                f"Array elements do not match '{base_type}' for var '{var_name}'"
                            )

                        scope[var_name] = declared_type
                        stmt.inferred_type = declared_type
                        stmt.variable.inferred_type = declared_type
                        expr.inferred_type = declared_type
                        self._mark_assigned(scope, var_name)
                        return

                    # else unify
                    unified = unify_types(declared_type, expr_type, for_assignment=True)
                    if unified != declared_type:
                        raise TypeError(
                            f"Cannot unify assignment: {expr_type} -> {declared_type}"
                        )
                    scope[var_name] = declared_type
                    stmt.inferred_type = declared_type
                    stmt.variable.inferred_type = declared_type
                    expr.inferred_type = declared_type
                    self._mark_assigned(scope, var_name)
                    return

                # Non-array expression unifying with array type
                unified = unify_types(declared_type, expr_type, for_assignment=True)
                if unified != declared_type:
                    raise TypeError(
                        f"Cannot unify assignment: {expr_type} -> {declared_type}"
                    )
                scope[var_name] = declared_type
                stmt.inferred_type = declared_type
                stmt.variable.inferred_type = declared_type
                expr.inferred_type = declared_type
                self._mark_assigned(scope, var_name)
                return

            # 2) If declared_type is NOT an array
            unified = unify_types(declared_type, expr_type, for_assignment=True)
            if unified != declared_type:
                raise TypeError(
                    f"Cannot assign '{expr_type}' to var of type '{declared_type}'"
                )
            scope[var_name] = declared_type
            stmt.inferred_type = declared_type
            stmt.variable.inferred_type = declared_type
            expr.inferred_type = declared_type
            self._mark_assigned(scope, var_name)

        else:
            # No declared type => infer from expr_type
            if expr_type == "array":
                if hasattr(expr, "elements") and expr.elements:
                    elem_type = self.dispatcher.check_expression(expr.elements[0], local_scope=scope)
                    for e in expr.elements[1:]:
                        e_type = self.dispatcher.check_expression(e, local_scope=scope)
                        elem_type = unify_types(elem_type, e_type, for_assignment=False)

                    final_type = (
                        elem_type + "[]"
                        if elem_type in ("int", "long", "float", "double", "string", "json")
                        else "array"
                    )
                    expr.inferred_type = final_type
                else:
                    final_type = "array"
                    expr.inferred_type = final_type

                scope[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type
                self._mark_assigned(scope, var_name)
                return

            elif expr_type == "json":
                if (
                    expr.type == "JsonLiteralExpression"
                    and isinstance(expr.value, list)
                    and expr.value
                ):
                    all_int = all(isinstance(v, int) for v in expr.value)
                    all_str = all(isinstance(v, str) for v in expr.value)
                    all_float = all(isinstance(v, float) or isinstance(v, int) for v in expr.value)

                    if all_int:
                        final_type = "int[]"
                    elif all_float and not all_str:
                        final_type = "float[]"
                    elif all_str:
                        final_type = "string[]"
                    else:
                        final_type = "json"

                    expr.inferred_type = final_type
                else:
                    final_type = "json"

                scope[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type
                self._mark_assigned(scope, var_name)

            else:
                final_type = expr_type
                scope[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type
                self._mark_assigned(scope, var_name)

    def _mark_assigned(self, scope: Dict[str, str], var_name: str) -> None:
        """
        Helper to mark var_name as assigned in the local scope's assigned-vars set.
        """
        assigned_vars = scope.get("__assigned_vars__", set())
        assigned_vars.add(var_name)
        scope["__assigned_vars__"] = assigned_vars
