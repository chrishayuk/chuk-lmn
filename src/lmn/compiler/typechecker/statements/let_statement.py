# file: lmn/compiler/typechecker/statements/let_statement.py

import logging
from typing import Dict

from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.utils import normalize_type, unify_types

logger = logging.getLogger(__name__)

def check_let_statement(stmt, symbol_table: Dict[str, str]) -> None:
    """
    Type check a 'let' statement and update the symbol table. Examples:
      let x: int = 5
      let typedNums: int[] = [1,2,3]
      let colors = [ "red", "green" ]   # now inferred as "string[]"
      let autoNums = [1, 2, 3]          # inferred as "int[]"
    """
    var_name = stmt.variable.name

    # Possibly "int", "int[]", "string[]", "float", "json", etc.
    type_annotation = getattr(stmt, "type_annotation", None)
    expr = stmt.expression

    logger.debug(f"Processing 'let' statement for variable '{var_name}'")
    logger.debug(f"Type annotation: {type_annotation}")

    declared_type = normalize_type(type_annotation) if type_annotation else None

    if expr:
        # 1) Expression => type-check with declared_type as a hint
        logger.debug(f"Type-checking expression for variable '{var_name}'.")
        expr_type = check_expression(expr, symbol_table, declared_type)
        logger.debug(f"Expression type for '{var_name}' => {expr_type}")

        if declared_type:
            # -------------------------------------------------------
            # A) If declared_type ends with "[]", handle typed array
            # -------------------------------------------------------
            if declared_type.endswith("[]"):
                base_type = declared_type[:-2]  # e.g. "int[]" => "int"

                # CASE 1: expression is a native ArrayLiteralExpression => expr_type == "array"
                if expr_type == "array":
                    # We'll ensure each element's .inferred_type == base_type
                    all_ok = True
                    if hasattr(expr, "elements"):
                        for element_expr in expr.elements:
                            elem_type = getattr(element_expr, "inferred_type", None)
                            if not elem_type:
                                # If expression checker didn't set it, we can unify again
                                elem_type = check_expression(element_expr, symbol_table)
                            # unify with base_type
                            unified = unify_types(base_type, elem_type, for_assignment=True)
                            if unified != base_type:
                                all_ok = False
                                break
                    else:
                        all_ok = False

                    if not all_ok:
                        raise TypeError(f"Array elements do not match '{base_type}' for var '{var_name}'")
                    
                    # If all good => final_type is declared_type (e.g. "string[]")
                    symbol_table[var_name] = declared_type
                    stmt.inferred_type = declared_type
                    stmt.variable.inferred_type = declared_type
                    expr.inferred_type = declared_type
                    return

                # CASE 2: expression is a JSON-literal array => expr_type == "json"
                elif expr_type == "json":
                    if expr.type == "JsonLiteralExpression" and isinstance(expr.value, list):
                        # We interpret expr.value as a Python list
                        all_ok = True
                        for val in expr.value:
                            if base_type == "int":
                                if not isinstance(val, int):
                                    all_ok = False
                                    break
                            elif base_type == "float":
                                # Accept float or int => float array
                                if not (isinstance(val, float) or isinstance(val, int)):
                                    all_ok = False
                                    break
                            elif base_type == "string":
                                if not isinstance(val, str):
                                    all_ok = False
                                    break
                            else:
                                # Potentially extend for 'long', 'bool', etc.
                                raise TypeError(f"Unsupported base type '{base_type}' in let statement.")

                        if not all_ok:
                            raise TypeError(
                                f"Array elements do not match '{base_type}' for var '{var_name}'"
                            )

                        # override 'json' => declared_type
                        symbol_table[var_name] = declared_type
                        stmt.inferred_type = declared_type
                        stmt.variable.inferred_type = declared_type
                        expr.inferred_type = declared_type
                        return

                    else:
                        # unify "json" with "string[]" => not possible
                        unified = unify_types(declared_type, expr_type, for_assignment=True)
                        if unified != declared_type:
                            raise TypeError(f"Cannot unify assignment: {expr_type} -> {declared_type}")

                        symbol_table[var_name] = declared_type
                        stmt.inferred_type = declared_type
                        stmt.variable.inferred_type = declared_type
                        expr.inferred_type = declared_type
                        return

                # CASE 3: Some other expr_type => unify normally
                # e.g. if we do let arr:int[] = someFnCall() which returns "int[]" 
                unified = unify_types(declared_type, expr_type, for_assignment=True)
                if unified != declared_type:
                    raise TypeError(
                        f"Cannot unify assignment: {expr_type} -> {declared_type}"
                    )
                # store final
                symbol_table[var_name] = declared_type
                stmt.inferred_type = declared_type
                stmt.variable.inferred_type = declared_type
                expr.inferred_type = declared_type
                return

            # -------------------------------------------------------
            # B) If declared_type is NOT an array
            # -------------------------------------------------------
            unified = unify_types(declared_type, expr_type, for_assignment=True)
            if unified != declared_type:
                raise TypeError(
                    f"Cannot assign '{expr_type}' to var of type '{declared_type}'"
                )
            symbol_table[var_name] = declared_type
            stmt.inferred_type = declared_type
            stmt.variable.inferred_type = declared_type
            expr.inferred_type = declared_type

        else:
            # -------------------------------------------
            # 2) No declared type => infer
            # -------------------------------------------
            # e.g. let colors = [ "red", "green", "blue" ]

            if expr_type == "array":
                # We have a native array => unify subexpressions
                # e.g. if all are "string", result => "string[]"
                # if all are "int", => "int[]"
                # if a mix of int/float => "float[]"?
                if hasattr(expr, "elements") and expr.elements:
                    # check the first element's type
                    elem_type = check_expression(expr.elements[0], symbol_table)
                    # unify the rest
                    for e in expr.elements[1:]:
                        e_type = check_expression(e, symbol_table)
                        elem_type = unify_types(elem_type, e_type, for_assignment=False)

                    # if elem_type is e.g. "string", final => "string[]"
                    final_type = elem_type + "[]" if elem_type in ("int","float","string") else "array"
                    expr.inferred_type = final_type
                else:
                    # empty array => "array"
                    final_type = "array"
                    expr.inferred_type = final_type

                symbol_table[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type
                return

            elif expr_type == "json":
                # bracket-literal => check if it's list
                if expr.type == "JsonLiteralExpression" and isinstance(expr.value, list) and expr.value:
                    # attempt uniform check
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

                symbol_table[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type

            else:
                # Not array or json => use expr_type directly
                final_type = expr_type
                symbol_table[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type

    else:
        # -------------------------------------------
        # 3) No expression => must have annotation or error
        # -------------------------------------------
        logger.debug(f"No expression for 'let {var_name}'.")
        if not declared_type:
            raise TypeError(
                f"No type annotation or initializer for '{var_name}' in let statement."
            )
        # store the declared type in the symbol table
        symbol_table[var_name] = declared_type
        stmt.variable.inferred_type = declared_type
        stmt.inferred_type = declared_type
        logger.debug(f"Marking '{var_name}' as '{declared_type}' in symbol table.")
