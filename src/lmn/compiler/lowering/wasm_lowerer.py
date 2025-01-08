# file: lmn/compiler/lowering/wasm_lowerer.py

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

##############################################################################
# 1) Mappings from language-level types to WASM-level (or pointer-level) types
##############################################################################

LANG_TO_WASM_SCALARS: Dict[str, str] = {
    "int":    "i32",
    "long":   "i64",
    "float":  "f32",
    "double": "f64",
    "f64":    "f64",        # Some DSLs explicitly say "f64" for double-precision
    "string": "i32_string",
    "i32_string": "i32_string",
    "json":   "i32_json",
}

LANG_TO_WASM_ARRAYS: Dict[str, str] = {
    "int[]":     "i32_ptr",
    "long[]":    "i64_ptr",
    "float[]":   "f32_ptr",
    "double[]":  "f64_ptr",
    "string[]":  "i32_string_array",
    "json[]":    "i32_json_array",
    # If the DSL uses "array" as a general untyped array:
    "array":     "i32_ptr",
}

##############################################################################
# 2) Convert a language-level type to WASM-level
##############################################################################

def lower_type(lang_type: Optional[str]) -> str:
    """
    Convert a language-level type string to a WASM-level type.
    e.g. "int[]" => "i32_ptr", "json" => "i32_json", "string" => "i32_string", etc.

    If `lang_type` is not a string (e.g. it's a dict for closures, or None),
    we'll return "i32" by default.
    """
    # If it's None or not a string, default to "i32"
    if not isinstance(lang_type, str):
        return "i32"

    # 1) If the entire type is in LANG_TO_WASM_ARRAYS
    if lang_type in LANG_TO_WASM_ARRAYS:
        return LANG_TO_WASM_ARRAYS[lang_type]

    # 2) If it's in LANG_TO_WASM_SCALARS
    if lang_type in LANG_TO_WASM_SCALARS:
        return LANG_TO_WASM_SCALARS[lang_type]

    # 3) If it ends with "[]", handle T[] => T_ptr
    if lang_type.endswith("[]"):
        base = lang_type[:-2]
        if base in LANG_TO_WASM_SCALARS:
            if base == "string":
                return "i32_string_array"
            elif base == "json":
                return "i32_json_array"
            else:
                return LANG_TO_WASM_SCALARS[base] + "_ptr"
        else:
            return "i32_ptr"  # unknown array => treat as i32_ptr

    # 4) Otherwise fallback to "i32"
    return "i32"


##############################################################################
# 3) The main lowering entry point for a Program node
##############################################################################

def lower_program_to_wasm_types(program_node: Any) -> None:
    """
    Called on the top-level 'Program' node to recursively lower every statement,
    converting .inferred_type / .type_annotation / .return_type from
    language-level types to WASM-level types.
    """
    logger.debug("lower_program_to_wasm_types: starting to process top-level body.")
    body = getattr(program_node, "body", [])
    for stmt in body:
        lower_node(stmt)


##############################################################################
# 4) Recursively lower a single AST node
##############################################################################

def lower_node(node: Any) -> None:
    """
    Recursively update node.inferred_type, node.type_annotation,
    node.return_type, and node.literal_type to WASM-level strings.
    Then descend into children (body, expressions, sub-nodes).
    """
    if not node:
        return

    node_type = getattr(node, "type", None)
    logger.debug(f"Visiting node: {node_type}")

    # A) If it's a LiteralExpression
    if node_type == "LiteralExpression":
        # 1) If no .inferred_type, fill it from .literal_type
        if getattr(node, "inferred_type", None) is None:
            lit_type = getattr(node, "literal_type", None)
            if lit_type:
                node.inferred_type = lower_type(lit_type)

        # 2) Also lower the .literal_type
        if hasattr(node, "literal_type") and node.literal_type:
            node.literal_type = lower_type(node.literal_type)

    # B) Lower node.inferred_type (if present)
    inferred = getattr(node, "inferred_type", None)
    if inferred is not None:
        node.inferred_type = lower_type(inferred)

    # C) Lower node.type_annotation (if present)
    if hasattr(node, "type_annotation") and node.type_annotation:
        node.type_annotation = lower_type(node.type_annotation)

    # D) If it's a FunctionDefinition => unify .return_type
    if node_type == "FunctionDefinition":
        if hasattr(node, "return_type") and node.return_type:
            node.return_type = lower_type(node.return_type)

    # -------------- Special cases or sub-fields --------------

    # Example: ConversionExpression => from_type, to_type, source_expr
    if node_type == "ConversionExpression":
        from_t = getattr(node, "from_type", None)
        if from_t:
            node.from_type = lower_type(from_t)
        to_t = getattr(node, "to_type", None)
        if to_t:
            node.to_type = lower_type(to_t)
        if getattr(node, "source_expr", None):
            lower_node(node.source_expr)

    # Example: FnExpression => reorder & lower children
    if node_type == "FnExpression":
        name_node = getattr(node, "name", None)
        # If name is itself a nested node/dict, we can recursively lower that
        if name_node and isinstance(name_node, dict):
            lower_node(name_node)

        # Also handle arguments
        if hasattr(node, "arguments"):
            for arg in node.arguments:
                lower_node(arg)

    # LetStatement => variable + expression
    if node_type == "LetStatement":
        if getattr(node, "variable", None):
            lower_node(node.variable)
        if getattr(node, "expression", None):
            lower_node(node.expression)

    # If the node has .expressions => lower them
    if hasattr(node, "expressions"):
        for expr in node.expressions:
            lower_node(expr)

    # If the node has a .body => lower each child
    if hasattr(node, "body") and node.body:
        for child in node.body:
            lower_node(child)

    # If the node has .params => they might have type_annotation
    if hasattr(node, "params"):
        for p in node.params:
            if getattr(p, "type_annotation", None):
                p.type_annotation = lower_type(p.type_annotation)
            if getattr(p, "inferred_type", None):
                p.inferred_type = lower_type(p.inferred_type)

    # E) If it's an AssignmentExpression => lower left & right
    if node_type == "AssignmentExpression":
        # Lower the node's own inferred_type
        if getattr(node, "inferred_type", None):
            node.inferred_type = lower_type(node.inferred_type)
        if getattr(node, "left", None):
            lower_node(node.left)
        if getattr(node, "right", None):
            lower_node(node.right)
        return

    # Generic fallback: handle .operand / .left / .right / .arguments
    if getattr(node, "operand", None):
        lower_node(node.operand)
    if getattr(node, "left", None):
        lower_node(node.left)
    if getattr(node, "right", None):
        lower_node(node.right)
    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

    # Example: IfStatement => condition, then_body, elseif_clauses, else_body
    if node_type == "IfStatement":
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

    if node_type == "ElseIfClause":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for st in node.body:
                lower_node(st)

    if node_type == "WhileStatement":
        if getattr(node, "condition", None):
            lower_node(node.condition)
        if getattr(node, "body", None):
            for st in node.body:
                lower_node(st)

    if node_type == "ReturnStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)

    if node_type == "AssignmentStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)
