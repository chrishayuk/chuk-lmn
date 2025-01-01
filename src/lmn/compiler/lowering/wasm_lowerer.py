# file: lmn/compiler/lowering/wasm_lowerer.py

from typing import Optional, Dict, Any

##############################################################################
# 1) Mappings from language-level types to WASM-level (or pointer-level) types
##############################################################################

LANG_TO_WASM_SCALARS: Dict[str, str] = {
    "int":      "i32",
    "long":     "i64",
    "float":    "f32",
    "double":   "f64",

    # You can treat "string" as an i32 pointer or keep it distinct:
    "string":   "i32_string",

    # JSON objects as i32 pointers:
    "json":     "i32_json",
}

LANG_TO_WASM_ARRAYS: Dict[str, str] = {
    "int[]":      "i32_ptr",
    "long[]":     "i64_ptr",
    "float[]":    "f32_ptr",
    "double[]":   "f64_ptr",

    # Strings in arrays:
    "string[]":   "i32_string_array",
    "json[]":     "i32_json_array",

    "array":      "i32_ptr"  # generic "array"
}

##############################################################################
# 2) Convert a language-level type to WASM-level
##############################################################################

def lower_type(lang_type: Optional[str]) -> str:
    """
    Convert a language-level type string (e.g. "int[]", "json", "string")
    to a WASM-level type (e.g. "i32_ptr", "i32_json", "i32_string").

    If unknown, defaults to "i32".
    """
    if not lang_type:
        return "i32"

    # 1. If the entire type is in LANG_TO_WASM_ARRAYS:
    if lang_type in LANG_TO_WASM_ARRAYS:
        return LANG_TO_WASM_ARRAYS[lang_type]

    # 2. If it's in LANG_TO_WASM_SCALARS:
    if lang_type in LANG_TO_WASM_SCALARS:
        return LANG_TO_WASM_SCALARS[lang_type]

    # 3. If it ends with "[]", handle T[] => T_ptr forms
    if lang_type.endswith("[]"):
        base_type = lang_type[:-2]
        if base_type in LANG_TO_WASM_SCALARS:
            if base_type == "string":
                return "i32_string_array"
            elif base_type == "json":
                return "i32_json_array"
            else:
                return LANG_TO_WASM_SCALARS[base_type] + "_ptr"
        else:
            return "i32_ptr"

    # 4. Otherwise fallback to "i32"
    return "i32"

##############################################################################
# 3) The main lowering entry point for a Program node
##############################################################################

def lower_program_to_wasm_types(program_node: Any) -> None:
    """
    Called on the top-level 'Program' node to recursively lower every statement.
    """
    body = getattr(program_node, "body", [])
    for stmt in body:
        lower_node(stmt)

##############################################################################
# 4) Recursively lower a single AST node
##############################################################################

def lower_node(node: Any) -> None:
    """
    Convert node.inferred_type / node.type_annotation (and now also 'return_type'
    for FunctionDefinition) to WASM-level strings, then recurse into child nodes.
    """

    # 1) Lower the node's own inferred_type
    inferred = getattr(node, "inferred_type", None)
    if inferred is not None:
        node.inferred_type = lower_type(inferred)

    # 2) Lower the node's type_annotation, if present
    if hasattr(node, "type_annotation") and node.type_annotation:
        node.type_annotation = lower_type(node.type_annotation)

    # 3) If it's a FunctionDefinition => unify .return_type too
    if node.type == "FunctionDefinition":
        if hasattr(node, "return_type") and node.return_type:
            node.return_type = lower_type(node.return_type)

    # 4) Special node-type handling

    # (A) ConversionExpression => from_type, to_type, source_expr
    if node.type == "ConversionExpression":
        from_t = getattr(node, "from_type", None)
        to_t   = getattr(node, "to_type", None)
        if from_t:
            node.from_type = lower_type(from_t)
        if to_t:
            node.to_type = lower_type(to_t)
        if getattr(node, "source_expr", None):
            lower_node(node.source_expr)

    # (B) FnExpression => lower 'name' if it's a nested dict, plus arguments
    if node.type == "FnExpression":
        maybe_name_node = getattr(node, "name", None)
        if maybe_name_node and isinstance(maybe_name_node, dict):
            lower_node(maybe_name_node)

        if hasattr(node, "arguments"):
            for arg in node.arguments:
                lower_node(arg)

    # (C) LetStatement => variable + expression
    if node.type == "LetStatement":
        if getattr(node, "variable", None):
            lower_node(node.variable)
        if getattr(node, "expression", None):
            lower_node(node.expression)
        # optionally node.inferred_type = "void"

    # (D) PrintStatement => node.expressions
    if hasattr(node, "expressions"):
        for expr in node.expressions:
            lower_node(expr)

    # (E) If the node has .body (Program, FunctionDefinition, BlockStatement)
    if hasattr(node, "body") and node.body:
        for child in node.body:
            lower_node(child)

    # (F) If the node has .params (function parameters)
    if hasattr(node, "params"):
        for p in node.params:
            # Lower param's type_annotation
            if getattr(p, "type_annotation", None):
                p.type_annotation = lower_type(p.type_annotation)
            # If param has p.inferred_type => lower it
            if getattr(p, "inferred_type", None):
                p.inferred_type = lower_type(p.inferred_type)
            # Typically parameters are leaf nodes

    # (G) Single-child expressions: operand / left / right
    if getattr(node, "operand", None):
        lower_node(node.operand)

    if getattr(node, "left", None):
        lower_node(node.left)

    if getattr(node, "right", None):
        lower_node(node.right)

    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

    # (H) IfStatement => condition, then_body, elseif_clauses, else_body
    if node.type == "IfStatement":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "then_body", None):
            for s in node.then_body:
                lower_node(s)
        if getattr(node, "elseif_clauses", None):
            for clause in node.elseif_clauses:
                lower_node(clause)
        if getattr(node, "else_body", None):
            for s in node.else_body:
                lower_node(s)
        # node.inferred_type = "void" if purely a statement

    if node.type == "ElseIfClause":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for st in node.body:
                lower_node(st)

    if node.type == "WhileStatement":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for st in node.body:
                lower_node(st)
        # node.inferred_type = "void"

    if node.type == "ReturnStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)
        # node.inferred_type = "void"

    if node.type == "AssignmentStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)
        # node.inferred_type = "void"

    # ------------------------------------------------------------------
    # Additional expansions (ForStatement, SwitchStatement, etc.) go here
    # ------------------------------------------------------------------
