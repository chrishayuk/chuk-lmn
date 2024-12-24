# src/lmn/compiler/typechecker/program_checker.py
from .function_checker import check_function_definition

def check_program(program_ast):
    # ensure the top level node is a program
    if program_ast.get("type") != "Program":
        raise TypeError("Top-level AST node must be 'Program'.")
    
    # get the body
    body = program_ast.get("body", [])

    # loop through each node in the body
    for node in body:
        # get the node
        node_type = node.get("type")

        # chck it's a function definition
        if node_type == "FunctionDefinition":
            # Check the function definition
            check_function_definition(node)
        else:
            # Potentially handle global variables or other top-level nodes
            raise NotImplementedError(f"Unsupported top-level node: {node_type}")
