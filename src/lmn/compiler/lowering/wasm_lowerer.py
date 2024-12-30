# file: lmn/compiler/lowering/wasm_lowerer.py

from typing import Optional, Dict

#
# 1) Mapping from language-level types (including typed arrays, JSON, etc.)
#    to WASM-level or pointer-level types.
#
#    - "int" => "i32"
#    - "float" => "f32"
#    - "double" => "f64"
#    - "int[]", "float[]" => e.g. "i32_ptr", "f32_ptr"
#    - "string[]" => "i32_ptr" (assuming you store strings in memory)
#    - "json" => "i32_json" (or "i32" if you prefer)
#    - "array" => "i32_ptr" for advanced bracket-literals
#
LANG_TO_WASM_MAP: Dict[str, str] = {
    "int":      "i32",
    "long":     "i64",
    "float":    "f32",
    "double":   "f64",

    # For typed arrays:
    "int[]":    "i32_ptr",   # handle/pointer to an int array
    "long[]":   "i64_ptr",
    "float[]":  "f32_ptr",
    "double[]": "f64_ptr",
    "string[]": "i32_ptr",   # or "string_ptr", if your runtime differs

    # For JSON objects/arrays you can store as references too:
    "json":     "i32_json",
    "array":    "i32_ptr",

    # IMPORTANT: Add this so single "string" is lowered to a pointer type, not i32
    "string":   "i32_ptr",
}


def lower_type(lang_type: Optional[str]) -> str:
    """
    Convert a single language-level type string to a WASM-level type or pointer type.
    If unknown, default to 'i32'.
    """
    if not lang_type:
        # If None or empty => default to i32
        return "i32"

    return LANG_TO_WASM_MAP.get(lang_type, "i32")


def lower_program_to_wasm_types(program_node):
    """
    Entry point for lowering the entire AST (program_node)
    to WASM-friendly types. Typically, program_node.type == "Program".
    """
    # Suppose program_node.body is a list of top-level items (function defs, statements, etc.)
    for stmt in program_node.body:
        lower_node(stmt)


def lower_node(node):
    """
    Recursively lower a single node (statement, expression, function, etc.)
    by converting node.inferred_type / node.type_annotation to the WASM-level string.

    Then visits child nodes (like .body, .params, etc.) to do the same.
    """

    # 1) If node has an inferred_type => map it to a WASM type
    inferred = getattr(node, "inferred_type", None)
    if inferred is not None:
        node.inferred_type = lower_type(inferred)

    # 2) If node has a type_annotation => map it
    if hasattr(node, "type_annotation") and node.type_annotation:
        node.type_annotation = lower_type(node.type_annotation)

    # 3) If node is a FunctionDefinition => handle return_type + param types
    if node.type == "FunctionDefinition":
        # If the node has return_type
        if getattr(node, "return_type", None):
            node.return_type = lower_type(node.return_type)

        # If the node has .params => each param has type_annotation
        if hasattr(node, "params") and node.params:
            for p in node.params:
                if p.type_annotation is None:
                    # default param => "int"
                    p.type_annotation = "int"
                p.type_annotation = lower_type(p.type_annotation)

    # (4) Recurse into child statements/expressions

    # If this is a block statement
    if node.type == "BlockStatement":
        # Recurse on node.statements
        if hasattr(node, "statements") and node.statements:
            for s in node.statements:
                lower_node(s)

    elif node.type == "LetStatement":
        # let var ...
        if node.variable:
            lower_node(node.variable)
        if node.expression:
            lower_node(node.expression)

    elif node.type == "AssignmentStatement":
        # x = expr
        if node.expression:
            lower_node(node.expression)

    elif node.type == "ReturnStatement":
        if node.expression:
            lower_node(node.expression)

    elif node.type == "IfStatement":
        # condition, then_body, elseif, else_body
        if getattr(node, "condition", None):
            lower_node(node.condition)

        if getattr(node, "then_body", None):
            for st in node.then_body:
                lower_node(st)

        if getattr(node, "elseif_clauses", None):
            for clause in node.elseif_clauses:
                lower_node(clause)

        if getattr(node, "else_body", None):
            for st in node.else_body:
                lower_node(st)

    elif node.type == "ElseIfClause":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for st in node.body:
                lower_node(st)

    elif node.type == "WhileStatement":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for st in node.body:
                lower_node(st)

    # If node has .body (like a function or block), handle it
    if hasattr(node, "body") and node.body:
        for sub_stmt in node.body:
            lower_node(sub_stmt)

    # If node has .params, handle them too (some statements might)
    if hasattr(node, "params"):
        for p in node.params:
            if p.type_annotation is None:
                p.type_annotation = "int"
            p.type_annotation = lower_type(p.type_annotation)

    # If it's an expression with operand/left/right/arguments
    if hasattr(node, "operand") and node.operand:
        lower_node(node.operand)

    if hasattr(node, "left") and node.left:
        lower_node(node.left)

    if hasattr(node, "right") and node.right:
        lower_node(node.right)

    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

    # If node has .expressions (like a PrintStatement):
    if hasattr(node, "expressions"):
        for expr in node.expressions:
            lower_node(expr)
