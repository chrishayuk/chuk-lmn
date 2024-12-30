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
            # -------------------------------------------
            # A) If declared_type ends with "[]", typed array logic
            # -------------------------------------------
            if declared_type.endswith("[]"):
                base_type = declared_type[:-2]  # e.g. "int[]" => "int"

                if expr_type == "json":
                    # Possibly a bracket-literal of uniform data
                    if expr.type == "JsonLiteralExpression" and isinstance(expr.value, list):
                        all_valid = True
                        for val in expr.value:
                            if base_type == "int":
                                if not isinstance(val, int):
                                    all_valid = False
                                    break
                            elif base_type == "float":
                                # Accept float or int => float array
                                if not (isinstance(val, float) or isinstance(val, int)):
                                    all_valid = False
                                    break
                            elif base_type == "string":
                                if not isinstance(val, str):
                                    all_valid = False
                                    break
                            else:
                                raise TypeError(
                                    f"Unsupported base type '{base_type}' in let statement."
                                )

                        if all_valid:
                            logger.debug(
                                f"Overriding 'json' => '{declared_type}' for '{var_name}' "
                                f"since all elements match '{base_type}'."
                            )
                            final_type = declared_type
                            # FIX: Also set the bracket-literal's inferred_type
                            stmt.expression.inferred_type = final_type

                            # Then unify the LetStatement
                            symbol_table[var_name] = final_type
                            stmt.inferred_type = final_type
                            stmt.variable.inferred_type = final_type
                            return
                        else:
                            raise TypeError(
                                f"Array elements do not match '{base_type}' for var '{var_name}'"
                            )

                    # If not a bracket-literal or mismatch => unify normally
                    unified = unify_types(declared_type, expr_type, for_assignment=True)
                    if unified != declared_type:
                        raise TypeError(
                            f"Cannot unify assignment: {expr_type} -> {declared_type}"
                        )
                    final_type = declared_type

                else:
                    # Not 'json' => unify normally
                    unified = unify_types(declared_type, expr_type, for_assignment=True)
                    if unified != declared_type:
                        raise TypeError(
                            f"Cannot unify assignment: {expr_type} -> {declared_type}"
                        )
                    final_type = declared_type

                # ensure we store final_type
                symbol_table[var_name] = final_type
                stmt.inferred_type = final_type
                stmt.variable.inferred_type = final_type
                return

            # -------------------------------------------
            # B) If declared_type is NOT an array
            # -------------------------------------------
            unified = unify_types(declared_type, expr_type, for_assignment=True)
            if unified != declared_type:
                raise TypeError(
                    f"Cannot assign '{expr_type}' to var of type '{declared_type}'"
                )
            final_type = declared_type

            symbol_table[var_name] = final_type
            stmt.inferred_type = final_type
            stmt.variable.inferred_type = final_type

        else:
            # -------------------------------------------
            # 3) No declared type => possibly infer typed array
            # -------------------------------------------
            if expr_type == "json":
                # bracket-literal => check uniform data
                if expr.type == "JsonLiteralExpression" and isinstance(expr.value, list) and expr.value:
                    all_int = all(isinstance(v, int) for v in expr.value)
                    all_str = all(isinstance(v, str) for v in expr.value)
                    all_float = all(isinstance(v, float) or isinstance(v, int) for v in expr.value)

                    if all_int:
                        final_type = "int[]"
                        stmt.expression.inferred_type = "int[]"
                    elif all_float and not all_str:
                        final_type = "float[]"
                        stmt.expression.inferred_type = "float[]"
                    elif all_str:
                        final_type = "string[]"
                        stmt.expression.inferred_type = "string[]"
                    else:
                        final_type = "json"
                else:
                    final_type = "json"
            else:
                # if expr_type is 'array' or something => no inference
                final_type = expr_type

            symbol_table[var_name] = final_type
            stmt.inferred_type = final_type
            stmt.variable.inferred_type = final_type
            logger.debug(f"Inferred final type for '{var_name}' => {final_type}")

    else:
        # -------------------------------------------
        # 4) No expression => must have annotation or error
        # -------------------------------------------
        logger.debug(f"No expression for 'let {var_name}'.")
        if not declared_type:
            raise TypeError(
                f"No type annotation or initializer for '{var_name}' in let statement."
            )
        # store
        symbol_table[var_name] = declared_type
        stmt.variable.inferred_type = declared_type
        stmt.inferred_type = declared_type
        logger.debug(f"Marking '{var_name}' as '{declared_type}' in symbol table.")
