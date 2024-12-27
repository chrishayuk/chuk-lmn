from lmn.compiler.ast.program import Program
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.function_checker import check_function_definition
from lmn.compiler.typechecker.statement_checker import check_statement
from typing import TYPE_CHECKING, Dict, Optional, Any
import logging
import traceback
from enum import Enum

if TYPE_CHECKING:
    from lmn.compiler.ast.statements import FunctionDefinition

# Configure logging
logger = logging.getLogger(__name__)

class TypeCheckError(Exception):
    """Custom exception for type checking errors with detailed information."""
    def __init__(self, message: str, node_type: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.node_type = node_type
        self.details = details or {}
        super().__init__(self.message)

def log_symbol_table(symbol_table: Dict[str, str]) -> None:
    """Log the current state of the symbol table."""
    logger.debug("Current symbol table state:")
    for var_name, var_type in symbol_table.items():
        logger.debug(f"  {var_name}: {var_type}")

def log_type_info(var_name: str, existing_type: Any, new_type: Any, symbol_table: Dict[str, str]) -> None:
    """Log detailed type information for debugging."""
    logger.debug(f"Type check info for variable '{var_name}':")
    logger.debug(f"  - Existing type: {existing_type} (type: {type(existing_type)})")
    logger.debug(f"  - New type: {new_type} (type: {type(new_type)})")
    logger.debug(f"  - Current symbol table entry: {symbol_table.get(var_name)}")

def type_check_program(program_node: Program) -> None:
    """
    The main entry point for type checking the entire AST.
    We assume program_node is an instance of Program with a .body that is a list of MegaUnion nodes.
    Each MegaUnion node has a .type (string) and other fields depending on the node type.
    Raises TypeError or NotImplementedError on mismatch.
    """
    logger.info("Starting type checking for program")
    
    try:
        symbol_table: Dict[str, str] = {}
        logger.debug("Initialized empty symbol table")

        for i, node in enumerate(program_node.body):
            logger.debug(f"Checking top-level node {i+1}/{len(program_node.body)}: {node.type}")
            logger.debug(f"Node details: {node.__dict__}")
            
            try:
                check_top_level_node(node, symbol_table)
                log_symbol_table(symbol_table)
            except Exception as e:
                logger.error(f"Error processing node {i+1}: {str(e)}")
                logger.error(f"Node that caused error: {node.__dict__}")
                raise
            
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

def check_top_level_node(node: Node, symbol_table: dict) -> None:
    """
    A top-level node might be a FunctionDefinition or a statement 
    (if your language allows statements at top-level). We'll dispatch accordingly.
    """
    node_type = node.type
    
    logger.debug(f"Processing node of type: {node_type}")
    logger.debug(f"Node attributes: {node.__dict__}")
    
    try:
        if node_type == "FunctionDefinition":
            logger.debug("Checking function definition")
            check_function_definition(node, symbol_table)
        else:
            logger.debug(f"Checking top-level statement: {node_type}")
            
            # Log expression details if present
            if hasattr(node, 'expression') and node.expression:
                expr = node.expression
                logger.debug(f"Expression to check: {expr.__dict__}")
                logger.debug(f"Expression type: {expr.type if hasattr(expr, 'type') else 'unknown'}")
                logger.debug(f"Expression inferred type: {expr.inferred_type if hasattr(expr, 'inferred_type') else 'none'}")
            
            # For assignments, log detailed type information
            if node_type == "AssignmentStatement":
                var_name = node.variable_name
                existing_type = symbol_table.get(var_name)
                
                if hasattr(node, 'type_annotation'):
                    logger.debug(f"Variable '{var_name}' has type annotation: {node.type_annotation}")
                
                log_type_info(var_name, 
                            existing_type,
                            getattr(node.expression, 'inferred_type', None) if hasattr(node, 'expression') else None,
                            symbol_table)
            
            check_statement(node, symbol_table)
            
    except (TypeError, NotImplementedError) as e:
        error_details = {
            "node_type": node_type,
            "symbol_table": symbol_table,
            "node_attributes": node.__dict__
        }
        logger.error(f"Error checking {node_type} node: {str(e)}", extra=error_details)
        raise TypeCheckError(str(e), node_type, error_details)
    except Exception as e:
        logger.critical(f"Unexpected error checking {node_type} node: {str(e)}")
        logger.critical(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
        raise