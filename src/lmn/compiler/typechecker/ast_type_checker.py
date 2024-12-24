# file: lmn/compiler/typechecker/ast_type_checker.py
from lmn.compiler.ast.program import Program
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.function_checker import check_function_definition
from lmn.compiler.typechecker.statement_checker import check_statement
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # If you want type hints for these classes, you can import them.
    from lmn.compiler.ast.statements import FunctionDefinition
    # etc.

def type_check_program(program_node: Program) -> None:
    """
    The main entry point for type checking the entire AST.
    We assume program_node is an instance of Program with a .body of MegaUnion nodes.
    Raises TypeError or NotImplementedError on mismatch.
    """
    symbol_table = {}
    for node in program_node.body:
        check_top_level_node(node, symbol_table)


def check_top_level_node(node: Node, symbol_table: dict) -> None:
    """
    A top-level node might be a FunctionDefinition or a statement 
    (if you allow statements at top-level). We'll dispatch accordingly.
    """
    node_type = node.type  # The 'type' from Pydantic

    if node_type == "FunctionDefinition":
        check_function_definition(node, symbol_table)
    else:
        # If your language allows top-level statements:
        # check_statement(node, symbol_table)
        # or else:
        raise NotImplementedError(f"Top-level node {node_type} not supported.")
