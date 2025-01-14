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
    Approach:
      - PASS 0a: Put top-level FunctionDefinition nodes into the symbol table,
                 storing param_names/param_types/param_defaults (ensuring matching lengths).
      - PASS 0b: Process top-level LetStatements (so closures, etc.) so they’re recognized.
      - Then unify param types from function calls, re-check function bodies, etc.
    """
    logger.info("Starting type checking for program")

    # ---------------------------------------------------------------
    # (A) Initialize symbol table with built-ins
    # ---------------------------------------------------------------
    symbol_table: Dict[str, Any] = {}

    for fn_name, fn_info in BUILTINS.items():
        symbol_table[fn_name] = fn_info

    # ---------------------------------------------------------------
    # (B) Convert 'typechecker.params' => param_names, param_types, param_defaults
    #     for built-ins (including zero-argument ones)
    # ---------------------------------------------------------------
    for fn_name, fn_info in symbol_table.items():
        # Pull out the typechecker info
        tc_info = fn_info.get("typechecker", {})
        params_list = tc_info.get("params", [])
        return_type = tc_info.get("return_type", "any")

        # If we truly have no param info AND no return type,
        # skip. But if there's at least a return type or an empty param list, handle it.
        if not params_list and return_type == "any":
            # Means we truly have no info
            continue

        param_names = []
        param_types = []
        param_defaults = []

        # Populate param info if any
        for pdef in params_list:
            p_name = pdef["name"]
            p_type = pdef.get("type", "any")
            p_required = pdef.get("required", False)
            p_default = pdef.get("default", None)

            param_names.append(p_name)
            param_types.append(p_type)

            if p_required and p_default is None:
                param_defaults.append(None)
            else:
                if p_default is not None:
                    # Wrap the default in a small LiteralExpression
                    default_expr = LiteralExpression(
                        type=NodeKind.LITERAL,
                        value=p_default,
                        literal_type="string",
                        inferred_type="string"
                    )
                    param_defaults.append(default_expr)
                else:
                    param_defaults.append(None)

        # Store final param + return info in symbol table
        fn_info["param_names"] = param_names
        fn_info["param_types"] = param_types
        fn_info["param_defaults"] = param_defaults
        fn_info["return_type"] = return_type
        symbol_table[fn_name] = fn_info

    try:
        function_nodes = []

        # Create dispatchers
        expr_dispatcher = ExpressionDispatcher(symbol_table)
        statement_dispatcher = StatementDispatcher(symbol_table, expr_dispatcher)

        # === PASS 0a: Insert top-level FunctionDefinition in symbol table
        logger.debug("=== PASS 0a: Pre-insert top-level FunctionDefinition names in symbol table ===")
        for node in program_node.body:
            if node.type == "FunctionDefinition":
                param_names, param_types, param_defaults = [], [], []
                for p in node.params:
                    param_names.append(p.name)
                    # We store None initially; partial unification can fill it
                    param_types.append(None)
                    param_defaults.append(None)

                rt = getattr(node, "return_type", None)
                symbol_table[node.name] = {
                    "is_function": True,
                    "param_names": param_names,
                    "param_types": param_types,
                    "param_defaults": param_defaults,
                    "return_type": rt
                }

        # === PASS 0b: Process top-level LetStatements
        logger.debug("=== PASS 0b: Process top-level let statements (closures, etc.) ===")
        for node in program_node.body:
            if node.type == "LetStatement":
                statement_dispatcher.check_statement(node)
                log_symbol_table(symbol_table)

        # === PASS 1: Gather function definitions & unify call param types
        logger.debug("=== PASS 1: Gather function definitions & unify call param types ===")
        for node in program_node.body:
            if node.type == "FunctionDefinition":
                function_nodes.append(node)

        unify_params_from_calls(program_node, symbol_table, expr_dispatcher)

        # === PASS 2: Re-check each stored function body
        logger.debug("=== PASS 2: Re-check each stored function body ===")
        for fn_node in function_nodes:
            logger.debug(f"Re-checking function: {fn_node.name}")
            func_def_checker = FunctionDefinitionChecker(symbol_table, statement_dispatcher)
            func_def_checker.check(fn_node)
            log_symbol_table(symbol_table)

        # === PASS 3: Check other top-level statements (besides FunctionDefinition, LetStatement)
        logger.debug("=== PASS 3: Check other top-level statements ===")
        for node in program_node.body:
            if node.type not in ("FunctionDefinition", "LetStatement"):
                statement_dispatcher.check_statement(node)
                log_symbol_table(symbol_table)

        # === PASS 4: Finalizing named => positional arguments
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
