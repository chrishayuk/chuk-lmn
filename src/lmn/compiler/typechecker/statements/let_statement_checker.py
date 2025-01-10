# file: lmn/compiler/typechecker/statements/let_statement_checker.py
import logging
from typing import Dict

# AST imports
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression  # Make sure FnExpression is accessible

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
        scope = local_scope if local_scope else self.symbol_table

        var_name = stmt.variable.name
        logger.debug(f"\n=== LetStatementChecker ===")
        logger.debug(f"Processing 'let' statement for variable '{var_name}'")

        # Possibly "int", "string[]", etc. Could be None if no annotation.
        type_annotation = getattr(stmt, "type_annotation", None)
        declared_type = normalize_type(type_annotation) if type_annotation else None
        logger.debug(f"Declared type annotation for '{var_name}': {declared_type}")

        expr = stmt.expression

        # A) No expression => must have annotation or raise error
        if not expr:
            logger.debug(f"No initializer expression for 'let {var_name}'. Checking if declared_type is required.")
            if not declared_type:
                raise TypeError(
                    f"No type annotation or initializer for '{var_name}' in let statement."
                )
            logger.debug(f"No expression => storing declared type '{declared_type}' for '{var_name}'.")
            scope[var_name] = declared_type
            stmt.variable.inferred_type = declared_type
            stmt.inferred_type = declared_type
            self._mark_assigned(scope, var_name)
            self._debug_symbol_tables(var_name, f"after storing declared type '{declared_type}' with no initializer")
            return

        # B) If expression is an AnonymousFunction => store closure
        if isinstance(expr, AnonymousFunctionExpression):
            logger.debug(f"Detected an inline AnonymousFunction for variable '{var_name}'")
            param_names, param_types = [], []
            for (p_name, p_type) in expr.parameters:
                param_names.append(p_name)
                # Provide a fallback if p_type isn't specified
                param_types.append(p_type or "int")

            # Create child scope
            function_scope = dict(scope)
            function_scope["__current_function_return_type__"] = expr.return_type or "void"
            assigned_vars = function_scope.get("__assigned_vars__", set())

            # Insert parameters into function_scope
            for i, p_name in enumerate(param_names):
                function_scope[p_name] = param_types[i]
                assigned_vars.add(p_name)
            function_scope["__assigned_vars__"] = assigned_vars

            # Type-check the inline function's body
            logger.debug(f"Type-checking body of the inline function assigned to '{var_name}'")
            for stmt_in_body in expr.body:
                self.dispatcher.check_statement(stmt_in_body, local_scope=function_scope)

            final_return_type = function_scope.get("__current_function_return_type__", "void")
            expr.return_type = final_return_type
            expr.inferred_type = "function"

            # Build closure info
            closure_info = {
                "is_closure": True,
                "param_names": param_names,
                "param_types": param_types,
                "return_type": final_return_type,
                "ast_node": expr
            }

            logger.debug(f"Storing inline closure for '{var_name}': {closure_info}")
            # Store in local scope + global symbol table
            scope[var_name] = closure_info
            self.symbol_table[var_name] = closure_info

            stmt.inferred_type = "function"
            stmt.variable.inferred_type = "function"
            self._mark_assigned(scope, var_name)
            self._debug_symbol_tables(var_name, "after storing an inline closure")
            return

        # C) If expression is a VariableExpression referencing a known function/closure
        if isinstance(expr, VariableExpression):
            rhs_name = expr.name
            logger.debug(f"Checking if '{rhs_name}' is a known function/closure in scope.")
            if rhs_name in scope:
                rhs_info = scope[rhs_name]
                # Confirm it's a dict describing a function or closure
                if (
                    isinstance(rhs_info, dict)
                    and (
                        rhs_info.get("is_closure")
                        or rhs_info.get("is_function")
                        or "param_names" in rhs_info
                    )
                ):
                    logger.debug(f"Aliasing function/closure '{rhs_name}' => new variable '{var_name}'")

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

                    logger.debug(
                        f"Storing alias info for '{var_name}': {alias_info}\n"
                        f"Also storing in self.symbol_table to ensure finalize pass won't skip it."
                    )
                    scope[var_name] = alias_info
                    self.symbol_table[var_name] = alias_info

                    final_type = "function"
                    stmt.inferred_type = final_type
                    stmt.variable.inferred_type = final_type
                    expr.inferred_type = final_type
                    self._mark_assigned(scope, var_name)
                    self._debug_symbol_tables(var_name, "after aliasing a known function/closure")
                    return
                else:
                    logger.debug(
                        f"RHS '{rhs_name}' found in scope but not recognized as function/closure; continuing normal flow..."
                    )

        # D) Otherwise => normal type-check logic
        logger.debug(f"Type-checking expression for variable '{var_name}'.")
        expr_type = self.dispatcher.check_expression(expr, target_type=declared_type, local_scope=scope)
        logger.debug(f"Expression type for '{var_name}' => {expr_type}")

        ### PATCH START ###
        # If this is a FnExpression but ended up 'void', see if we can override it using the symbol_table
        if isinstance(expr, FnExpression) and expr_type == "void":
            fn_name_node = getattr(expr, "name", None)
            if fn_name_node and hasattr(fn_name_node, "name"):
                fn_name = fn_name_node.name
                fn_info = self.symbol_table.get(fn_name, None)
                if isinstance(fn_info, dict):
                    # Check if there's a declared return_type
                    fn_return = fn_info.get("return_type", None)
                    if fn_return and fn_return != "void":
                        logger.debug(
                            f"[Patch] Overriding expr_type='void' => '{fn_return}' "
                            f"for FnExpression call to '{fn_name}'"
                        )
                        expr_type = fn_return
                        expr.inferred_type = fn_return
        ### PATCH END ###

        # If we got a closure dictionary, store it
        if isinstance(expr_type, dict) and expr_type.get("is_closure"):
            logger.debug(
                f"'{var_name}' is assigned a closure dictionary with "
                f"param_types={expr_type.get('param_types')} and return_type={expr_type.get('return_type')}.\n"
                f"Storing in both scope and self.symbol_table."
            )
            scope[var_name] = expr_type
            self.symbol_table[var_name] = expr_type

            stmt.inferred_type = "function"
            stmt.variable.inferred_type = "function"
            expr.inferred_type = "function"
            self._mark_assigned(scope, var_name)
            self._debug_symbol_tables(var_name, "after storing a closure dictionary from normal type-check logic")
            return

        #
        # If not a closure, unify or store type as normal
        #
        if declared_type:
            # If declared_type ends with "[]", handle typed arrays
            if declared_type.endswith("[]"):
                base_type = declared_type[:-2]
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

                    logger.debug(f"Storing typed array '{declared_type}' for '{var_name}'.")
                    scope[var_name] = declared_type
                    stmt.inferred_type = declared_type
                    stmt.variable.inferred_type = declared_type
                    expr.inferred_type = declared_type
                    self._mark_assigned(scope, var_name)
                    self._debug_symbol_tables(var_name, f"after storing typed array '{declared_type}'")
                    return

                elif expr_type == "json":
                    # Possibly a JSON-literal array => check elements
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
                                raise TypeError(f"Unsupported base type '{base_type}' in let statement.")

                        if not all_ok:
                            raise TypeError(
                                f"Array elements do not match '{base_type}' for var '{var_name}'"
                            )

                        logger.debug(f"Storing typed array '{declared_type}' from JSON-literal for '{var_name}'.")
                        scope[var_name] = declared_type
                        stmt.inferred_type = declared_type
                        stmt.variable.inferred_type = declared_type
                        expr.inferred_type = declared_type
                        self._mark_assigned(scope, var_name)
                        self._debug_symbol_tables(var_name, f"after storing typed array from JSON-literal '{declared_type}'")
                        return

                    # else unify
                    unified = unify_types(declared_type, expr_type, for_assignment=True)
                    if unified != declared_type:
                        raise TypeError(f"Cannot unify assignment: {expr_type} -> {declared_type}")

                    scope[var_name] = declared_type
                    stmt.inferred_type = declared_type
                    stmt.variable.inferred_type = declared_type
                    expr.inferred_type = declared_type
                    self._mark_assigned(scope, var_name)
                    self._debug_symbol_tables(var_name, f"after unify JSON -> declared_type '{declared_type}'")
                    return

                # Non-array expression unifying with array type => unify
                unified = unify_types(declared_type, expr_type, for_assignment=True)
                if unified != declared_type:
                    raise TypeError(f"Cannot assign '{expr_type}' to var of type '{declared_type}'")

                logger.debug(f"Storing array type '{declared_type}' for '{var_name}'.")
                scope[var_name] = declared_type
                stmt.inferred_type = declared_type
                stmt.variable.inferred_type = declared_type
                expr.inferred_type = declared_type
                self._mark_assigned(scope, var_name)
                self._debug_symbol_tables(var_name, f"after unify declared array type '{declared_type}'")
                return

            # declared_type is NOT an array => unify
            unified = unify_types(declared_type, expr_type, for_assignment=True)
            if unified != declared_type:
                raise TypeError(f"Cannot assign '{expr_type}' to var of type '{declared_type}'")

            # === Insert a ConversionExpression for string->numeric if needed
            if declared_type in ("int", "long", "float", "double") and expr_type == "string":
                from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression

                conversion_expr = ConversionExpression(
                    from_type="string",
                    to_type=declared_type,
                    source_expr=stmt.expression,
                    inferred_type=declared_type
                )
                stmt.expression = conversion_expr
                logger.debug(f"Inserted ConversionExpression for string->'{declared_type}'")

            logger.debug(f"Storing declared type '{declared_type}' for '{var_name}'.")
            scope[var_name] = declared_type
            stmt.inferred_type = declared_type
            stmt.variable.inferred_type = declared_type
            expr.inferred_type = declared_type
            self._mark_assigned(scope, var_name)
            self._debug_symbol_tables(var_name, f"after unify declared type '{declared_type}'")

        else:
            # No declared type => infer from expr_type
            if expr_type == "array":
                logger.debug(f"Inferring array type for '{var_name}'.")
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

                logger.debug(f"Storing inferred array type '{expr.inferred_type}' for '{var_name}'.")
                scope[var_name] = expr.inferred_type
                stmt.inferred_type = expr.inferred_type
                stmt.variable.inferred_type = expr.inferred_type
                self._mark_assigned(scope, var_name)
                self._debug_symbol_tables(var_name, f"after inferring array type '{expr.inferred_type}'")
                return

            elif expr_type == "json":
                logger.debug(f"Inferring json type for '{var_name}'.")
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

                logger.debug(f"Storing inferred json-based type '{final_type}' for '{var_name}'.")
                scope[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type
                self._mark_assigned(scope, var_name)
                self._debug_symbol_tables(var_name, f"after inferring json-based type '{final_type}'")

            else:
                # Just store it as final_type (whatever expr_type was)
                logger.debug(f"Inferring type '{expr_type}' for '{var_name}'.")
                scope[var_name] = expr_type
                stmt.inferred_type = expr_type
                stmt.variable.inferred_type = expr_type
                self._mark_assigned(scope, var_name)
                self._debug_symbol_tables(var_name, f"after inferring normal type '{expr_type}'")

    def _mark_assigned(self, scope: Dict[str, str], var_name: str) -> None:
        assigned_vars = scope.get("__assigned_vars__", set())
        assigned_vars.add(var_name)
        scope["__assigned_vars__"] = assigned_vars
        logger.debug(
            f"Marked '{var_name}' as assigned in scope; assigned_vars now: {assigned_vars}"
        )

    def _debug_symbol_tables(self, var_name: str, context_msg: str) -> None:
        """
        Helper to dump relevant local scope + global symbol_table 
        for extended debugging after we store a function/closure or do a unify.
        """
        logger.debug(f"[{context_msg}] Current local scope keys: {list(self.symbol_table.keys())}")
        if var_name in self.symbol_table:
            logger.debug(f"[{context_msg}] self.symbol_table['{var_name}'] => {self.symbol_table[var_name]}")
        else:
            logger.debug(f"[{context_msg}] '{var_name}' not in self.symbol_table at all.")
