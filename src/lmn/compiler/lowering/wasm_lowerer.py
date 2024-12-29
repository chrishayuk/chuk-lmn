# file: lmn/compiler/lowering/wasm_lowerer.py

from typing import Optional, Dict

LANG_TO_WASM_MAP: Dict[str, str] = {
    "int":    "i32",
    "long":   "i64",
    "float":  "f32",
    "double": "f64",
}


def lower_type(lang_type: Optional[str]) -> str:
    """
    Convert a single language-level type to WASM-level type.
    If unknown, default to 'i32'.
    """
    if not lang_type:
        # If it's None or empty, treat it as i32
        return "i32"
    return LANG_TO_WASM_MAP.get(lang_type, "i32")


def lower_program_to_wasm_types(program_node):
    """
    Entry point for lowering the entire AST (program_node)
    to WASM-friendly types. Typically, program_node.type == "Program".
    """
    # program_node.body is a list of top-level statements or FunctionDefinitions
    for stmt in program_node.body:
        lower_node(stmt)


def lower_node(node):
    """
    Recursively lower a single node (statement, expression, function, etc.).
    This function checks node.type or node fields, then visits sub-nodes.
    """

    # 1) If the node has inferred_type, convert it to WASM type
    inferred = getattr(node, "inferred_type", None)
    if inferred:
        node.inferred_type = lower_type(inferred)

    # 2) If the node has a type_annotation (e.g., param, let-statement), convert it
    if hasattr(node, "type_annotation") and node.type_annotation:
        node.type_annotation = lower_type(node.type_annotation)

    # 3) If the node is a FunctionDefinition, handle params and return_type
    if node.type == "FunctionDefinition":
        # If there's a declared return_type, lower it
        if getattr(node, "return_type", None):
            node.return_type = lower_type(node.return_type)

        # If the function has .params, ensure each param has a type_annotation != None
        if hasattr(node, "params"):
            for p in node.params:
                # If param has no annotation, default to "int" => "i32"
                if p.type_annotation is None:
                    p.type_annotation = "int"
                # Now lower it
                p.type_annotation = lower_type(p.type_annotation)

    # ---- Recursively handle known node types ----

    if node.type == "BlockStatement":
        # e.g., node.statements is a list of statements
        if hasattr(node, "statements") and node.statements:
            for s in node.statements:
                lower_node(s)

    elif node.type == "LetStatement":
        # LetStatement might have .variable, .expression
        if node.variable:
            lower_node(node.variable)
        if node.expression:
            lower_node(node.expression)

    elif node.type == "AssignmentStatement":
        # assignment: x = expr
        if node.expression:
            lower_node(node.expression)

    elif node.type == "ReturnStatement":
        if node.expression:
            lower_node(node.expression)

    elif node.type == "IfStatement":
        # Handle condition
        if getattr(node, "condition", None):
            lower_node(node.condition)

        # Handle then_body
        if getattr(node, "then_body", None):
            for s in node.then_body:
                lower_node(s)

        # Handle elseif_clauses
        if getattr(node, "elseif_clauses", None):
            for clause in node.elseif_clauses:
                lower_node(clause)

        # Handle else_body
        if getattr(node, "else_body", None):
            for s in node.else_body:
                lower_node(s)

    elif node.type == "ElseIfClause":
        # If you treat ElseIfClause as a distinct node type:
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for st in node.body:
                lower_node(st)

    elif node.type == "WhileStatement":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for s in node.body:
                lower_node(s)

    # 4) If the node has a generic .body field (like a FunctionDefinition),
    #    we should also recurse
    if hasattr(node, "body") and node.body:
        for sub_stmt in node.body:
            lower_node(sub_stmt)

    # 5) Even outside a FunctionDefinition, if node has .params, handle them
    if hasattr(node, "params"):
        for p in node.params:
            if p.type_annotation is None:
                p.type_annotation = "int"
            p.type_annotation = lower_type(p.type_annotation)

    # 6) If the node is an expression with .left, .right, .arguments, etc.
    if hasattr(node, "left") and node.left:
        lower_node(node.left)
    if hasattr(node, "right") and node.right:
        lower_node(node.right)
    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

    # 7) If the node has .expressions (like a PrintStatement)
    if hasattr(node, "expressions"):
        for expr in node.expressions:
            lower_node(expr)
