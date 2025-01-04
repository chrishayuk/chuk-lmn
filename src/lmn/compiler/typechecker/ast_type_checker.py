# file: lmn/compiler/typechecker/ast_type_checker.py

import logging
import traceback
from typing import Dict, Any

# 1) Import the built-in definitions
from lmn.builtins import BUILTINS
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.program import Program
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.typechecker.finalize_arguments_pass import finalize_function_calls
from lmn.compiler.typechecker.function_call_type_unifier import unify_params_from_calls
from lmn.compiler.typechecker.utils import unify_types
from lmn.compiler.typechecker.expressions.expression_dispatcher import ExpressionDispatcher

# statement and expression checkers
from lmn.compiler.typechecker.statements.statement_dispatcher import StatementDispatcher
from lmn.compiler.typechecker.statements.function_definition_checker import FunctionDefinitionChecker

logger = logging.getLogger(__name__)

class TypeCheckError(Exception):
    """Custom exception for type checking errors with detailed information."""
    def __init__(self, message: str, node_type: str = None, details: dict = None):
        self.message = message
        self.node_type = node_type
        self.details = details or {}
        super().__init__(self.message)

def log_symbol_table(symbol_table: Dict[str, Any]) -> None:
    logger.debug("Current symbol table state:")
    for var_name, var_type in symbol_table.items():
        logger.debug(f"  {var_name}: {var_type}")

def type_check_program(program_node: Program) -> None:
    """
    A multi-step approach:
      1) Gather function definitions into the symbol table
      2) Partially unify param types from calls (FnExpressions)
      3) Re-check each stored FunctionDefinition body (param types are known)
      4) Check other top-level statements
      5) Finalize named => positional arguments
    """
    logger.info("Starting type checking for program")

    # ---------------------------------------------------------------
    # (A) Initialize symbol table with built-ins
    # ---------------------------------------------------------------
    symbol_table: Dict[str, Any] = {}

    for fn_name, fn_info in BUILTINS.items():
        symbol_table[fn_name] = fn_info

    # ---------------------------------------------------------------
    # (B) Convert "typechecker.params" => param_names, param_types, param_defaults
    # ---------------------------------------------------------------
    for fn_name, fn_info in symbol_table.items():
        # Pull out the typechecker info
        tc_info = fn_info.get("typechecker", {})
        params_list = tc_info.get("params", [])
        return_type = tc_info.get("return_type", "any")

        # If there's no params, skip
        if not params_list:
            continue

        param_names = []
        param_types = []
        param_defaults = []

        # Build up the param data
        for pdef in params_list:
            p_name = pdef["name"]
            p_type = pdef.get("type", "any")
            p_required = pdef.get("required", False)
            p_default = pdef.get("default", None)

            # Store param name and type
            param_names.append(p_name)
            param_types.append(p_type)

            # Decide how to store the default
            if p_required and p_default is None:
                # No default for a required param
                param_defaults.append(None)
            else:
                # If there's a default, store an actual AST node
                if p_default is not None:
                    # Create a LiteralExpression node
                    default_expr = LiteralExpression(
                        type=NodeKind.LITERAL,      # or "LiteralExpression"
                        value=p_default,
                        literal_type="string",
                        inferred_type="string"      # optional
                    )
                    param_defaults.append(default_expr)
                else:
                    param_defaults.append(None)

        # Assign them into the fn_info for the finalize pass
        fn_info["param_names"] = param_names
        fn_info["param_types"] = param_types
        fn_info["param_defaults"] = param_defaults

        # Also store return_type if needed
        fn_info["return_type"] = return_type

        # Put back
        symbol_table[fn_name] = fn_info

    try:
        # We'll collect all FunctionDefinition nodes to re-check them after unification
        function_nodes = []

        # ExpressionDispatcher for expressions
        expr_dispatcher = ExpressionDispatcher(symbol_table)

        # === PASS 1: Gather function definitions & unify param types from calls
        logger.debug("=== PASS 1: Gather function definitions & unify call param types ===")
        for node in program_node.body:
            if node.type == "FunctionDefinition":
                param_types = []
                for p in node.params:
                    declared = getattr(p, "type_annotation", None)
                    param_types.append(declared)

                rt = getattr(node, "return_type", None)

                # Temporarily store partial info in the symbol_table for user-defined funcs
                symbol_table[node.name] = {
                    "param_types": param_types,
                    "return_type": rt
                }
                function_nodes.append(node)

        # Attempt partial unification from function calls
        unify_params_from_calls(program_node, symbol_table, expr_dispatcher)

        # === PASS 2: Re-check each stored function body
        logger.debug("=== PASS 2: Re-check each stored function body ===")
        statement_dispatcher = StatementDispatcher(symbol_table, expr_dispatcher)

        for fn_node in function_nodes:
            logger.debug(f"Re-checking function: {fn_node.name}")
            func_def_checker = FunctionDefinitionChecker(symbol_table, statement_dispatcher)
            func_def_checker.check(fn_node)
            log_symbol_table(symbol_table)

        # === PASS 3: Check other top-level statements
        logger.debug("=== PASS 3: Check other top-level statements ===")
        for node in program_node.body:
            if node.type != "FunctionDefinition":
                statement_dispatcher.check_statement(node)
                log_symbol_table(symbol_table)

        # === PASS 4: Finalizing named arguments => positional
        logger.debug("=== PASS 4: Finalizing named arguments => positional ===")
        finalize_function_calls(program_node, symbol_table)

        logger.info("Type checking completed successfully")

    except TypeCheckError as e:
        logger.error(f"Type checking failed: {e.message}")
        if e.details:
            logger.error(f"Error details: {e.details}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error during type checking: {str(e)}")
        logger.critical(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
        raise
