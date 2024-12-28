# file: lmn/compiler/lowering/wasm_lowerer.py
from typing import Union

# A simple map from language-level to WASM-level
LANG_TO_WASM_MAP = {
    "int":    "i32",
    "long":   "i64",
    "float":  "f32",
    "double": "f64",
}

def lower_type(lang_type: str) -> str:
    """
    Convert a single language-level type to WASM-level type.
    If unknown, default to 'i32' or raise an error.
    """
    return LANG_TO_WASM_MAP.get(lang_type, "i32")

def lower_program_to_wasm_types(program_node):
    """
    Recursively walk the entire AST (Program node) and 
    convert each node's 'inferred_type' or 'type_annotation' 
    from language-level to WASM-level types.
    """
    # e.g. program_node.body is a list of statements or FunctionDefinition
    for stmt in program_node.body:
        lower_node(stmt)

def lower_node(node):
    # 1) Convert node.inferred_type if present
    if getattr(node, "inferred_type", None):
        node.inferred_type = lower_type(node.inferred_type)

    # 2) Convert node.type_annotation if present
    if hasattr(node, "type_annotation") and node.type_annotation:
        node.type_annotation = lower_type(node.type_annotation)

    # 3) If it's a FunctionDefinition, handle return_type
    if node.type == "FunctionDefinition" and getattr(node, "return_type", None):
        node.return_type = lower_type(node.return_type)

    # 4) If it's a LetStatement, handle node.variable
    if node.type == "LetStatement":
        if node.variable:
            lower_node(node.variable)
        if node.expression:
            lower_node(node.expression)

    # For an AssignmentStatement, you might need to lower the RHS expression
    if node.type == "AssignmentStatement":
        # there's no direct node.variable AST, just a variable_name string, 
        # so you only need to lower node.expression
        if node.expression:
            lower_node(node.expression)

    # Similarly for ReturnStatement, handle node.expression
    if node.type == "ReturnStatement":
        if node.expression:
            lower_node(node.expression)

    # If node has a .body (like a function or a block), recurse
    if hasattr(node, "body") and node.body:
        for sub_stmt in node.body:
            lower_node(sub_stmt)

    # If node has .params, each param might have a type_annotation
    if hasattr(node, "params"):
        for p in node.params:
            if p.type_annotation:
                p.type_annotation = lower_type(p.type_annotation)
            # no need for inferred_type if your param nodes don’t store it

    # If it’s an expression with .left, .right, .arguments, etc.
    if hasattr(node, "left") and node.left:
        lower_node(node.left)
    if hasattr(node, "right") and node.right:
        lower_node(node.right)
    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

    # If it has .expressions (like PrintStatement)
    if hasattr(node, "expressions"):
        for expr in node.expressions:
            lower_node(expr)
