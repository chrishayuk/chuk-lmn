# file: lmn/compiler/typechecker/ast_type_checker.py

import logging
import traceback
from typing import Dict, Any

# 1) Import the built-in definitions
from lmn.compiler.ast.program import Program
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.finalize_arguments_pass import finalize_function_calls
from lmn.compiler.typechecker.builtins import BUILTIN_FUNCTIONS
from lmn.compiler.typechecker.function_call_type_unifier import unify_params_from_calls
from lmn.compiler.typechecker.utils import unify_types
from lmn.compiler.typechecker.expressions.expression_dispatcher import ExpressionDispatcher

# statement and expression checkerss
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
      1) Gather function definitions into the symbol table, store them in a list
      2) Partially unify param types from calls (FnExpressions)
      3) Re-check each stored FunctionDefinition body (now that param types are known)
      4) Finally, check other top-level statements
    """
    logger.info("Starting type checking for program")
    
    # ---------------------------------------------------------------
    # 1) Initialize symbol table with built-ins
    # ---------------------------------------------------------------
    symbol_table: Dict[str, Any] = {}
    for fn_name, fn_sig in BUILTIN_FUNCTIONS.items():
        symbol_table[fn_name] = fn_sig

    # ---------------------------------------------------------------
    # 1a) [FIX] Convert required_params/optional_params => param_names/param_defaults
    #     for each built-in function so finalize_function_calls can reorder arguments properly.
    # ---------------------------------------------------------------
    for fn_name, fn_info in symbol_table.items():
        required_params = fn_info.get("required_params", {})
        optional_params = fn_info.get("optional_params", {})

        if not required_params and not optional_params:
            continue

        param_names = list(required_params.keys()) + list(optional_params.keys())
        param_defaults = [None] * len(required_params) + [None] * len(optional_params)

        fn_info["param_names"] = param_names
        fn_info["param_defaults"] = param_defaults

        symbol_table[fn_name] = fn_info

    try:
        # We'll collect all FunctionDefinition nodes to re-check them after we unify calls
        function_nodes = []

        # Create an ExpressionDispatcher for expressions
        expr_dispatcher = ExpressionDispatcher(symbol_table)

        # Step 1: Gather function definitions & unify param types from calls
        logger.debug("=== PASS 1: Gather function definitions & unify call param types ===")
        for node in program_node.body:
            if node.type == "FunctionDefinition":
                param_types = []
                for p in node.params:
                    declared = getattr(p, "type_annotation", None)
                    param_types.append(declared)

                rt = getattr(node, "return_type", None)

                # Temporarily store partial info in the symbol_table
                symbol_table[node.name] = {
                    "param_types": param_types,
                    "return_type": rt
                }
                function_nodes.append(node)

        # Attempt partial unification from function calls
        unify_params_from_calls(program_node, symbol_table, expr_dispatcher)

        # Step 2: Re-check each stored function body (with updated param info)
        logger.debug("=== PASS 2: Re-check each stored function body ===")
        
        # We create a StatementDispatcher for non-function statements
        statement_dispatcher = StatementDispatcher(symbol_table, expr_dispatcher)

        # loop through the stored function nodes
        for fn_node in function_nodes:
            logger.debug(f"Re-checking function: {fn_node.name}")
            # Create a FunctionDefinitionChecker for each function node
            func_def_checker = FunctionDefinitionChecker(symbol_table, statement_dispatcher)

            # Check the function body
            func_def_checker.check(fn_node)

            # log the symbol table
            log_symbol_table(symbol_table)

        # Step 3: Check other top-level statements (that aren't function definitions)
        logger.debug("=== PASS 3: Check other top-level statements ===")
        for node in program_node.body:
            if node.type != "FunctionDefinition":
                # Let the StatementDispatcher route them
                statement_dispatcher.check_statement(node)

                # log the symbol table
                log_symbol_table(symbol_table)

        # Step 4: Finalizing named arguments => positional
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



