# file: lmn/compiler/typechecker/ast_type_checker.py
from lmn.compiler.ast.program import Program
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.function_checker import check_function_definition
from lmn.compiler.typechecker.statement_checker import check_statement
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    # If you want type hints for these classes, you can import them.
    from lmn.compiler.ast.statements import FunctionDefinition
    # etc.

def type_check_program(program_node: Program) -> None:
    """
    The main entry point for type checking the entire AST.
    We assume program_node is an instance of Program with a .body that is a list of MegaUnion nodes.
    Each MegaUnion node has a .type (string) and other fields depending on the node type.
    Raises TypeError or NotImplementedError on mismatch.
    """

    # You can keep a single symbol table or multiple scopes if your language requires.
    symbol_table: Dict[str, str] = {}

    # Iterate over all top-level nodes
    for node in program_node.body:
        check_top_level_node(node, symbol_table)


def check_top_level_node(node: Node, symbol_table: dict) -> None:
    """
    A top-level node might be a FunctionDefinition or a statement 
    (if your language allows statements at top-level). We'll dispatch accordingly.
    """
    # get the node type
    node_type = node.type  # 'FunctionDefinition', 'PrintStatement', etc.

    if node_type == "FunctionDefinition":
        # Dispatch to function checker
        check_function_definition(node, symbol_table)
    else:
        # Any other node type is treated as a statement at top-level
        check_statement(node, symbol_table)
