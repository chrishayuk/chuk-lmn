# file: lmn/compiler/lowering/wasm_lowerer.py

from typing import Optional, Dict, Any

##############################################################################
# 1) Mappings from language-level types to WASM-level (or pointer-level) types
##############################################################################

LANG_TO_WASM_SCALARS: Dict[str, str] = {
    "int":        "i32",
    "long":       "i64",
    "float":      "f32",
    "double":     "f64",

    # If your DSL or typechecker uses the literal string "f64" 
    # to indicate a double-precision float, add this:
    "f64":        "f64",

    "string":     "i32_string",
    "i32_string": "i32_string",
    "json":       "i32_json",
}


LANG_TO_WASM_ARRAYS: Dict[str, str] = {
    "int[]":      "i32_ptr",
    "long[]":     "i64_ptr",
    "float[]":    "f32_ptr",
    "double[]":   "f64_ptr",
    "string[]":   "i32_string_array",
    "json[]":     "i32_json_array",
    "array":      "i32_ptr"
}

##############################################################################
# 2) Convert a language-level type to WASM-level
##############################################################################

def lower_type(lang_type: Optional[str]) -> str:
    """
    Convert a language-level type string to a WASM-level type
    (e.g. "int[]" => "i32_ptr", "json" => "i32_json", "string" => "i32_string").

    If unknown, defaults to "i32".
    """
    if not lang_type:
        return "i32"

    # 1) If the entire type is in LANG_TO_WASM_ARRAYS:
    if lang_type in LANG_TO_WASM_ARRAYS:
        return LANG_TO_WASM_ARRAYS[lang_type]

    # 2) If it's in LANG_TO_WASM_SCALARS:
    if lang_type in LANG_TO_WASM_SCALARS:
        return LANG_TO_WASM_SCALARS[lang_type]

    # 3) If it ends with "[]", handle T[] => T_ptr forms
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

    # 4) Otherwise fallback to "i32"
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
    Convert node.inferred_type / node.type_annotation / node.return_type
    and also node.literal_type for literals, to WASM-level strings.
    Then recurse into child nodes.
    """

    # A) Safely extract the node's 'type' field (if any)
    nodetype = getattr(node, "type", None)
    if not nodetype:
        # This node doesn't define 'type' => skip or handle generically
        return

    # ------------------------------------------------------------------------
    # A) If it's a LiteralExpression, we do two things:
    #    1) If .inferred_type is None, fill it from .literal_type (converted).
    #    2) Then also lower .literal_type itself, so it's no longer "string"/"f64"/etc.
    # ------------------------------------------------------------------------
    if node.type == "LiteralExpression":

        # 1) If .inferred_type is missing, fill from .literal_type
        if getattr(node, "inferred_type", None) is None:
            lit_type = getattr(node, "literal_type", None)
            if lit_type:
                # Convert "string" => "i32_string", "f64" => "f64", etc.
                lowered_lit_type = lower_type(lit_type)
                node.inferred_type = lowered_lit_type  # e.g. "i32_string"

        # 2) Also lower the existing literal_type field itself
        #    so it doesn't stay "string"/"f64". 
        #    If you prefer to *remove* literal_type from the AST, do:
        #
        #    if hasattr(node, "literal_type"):
        #        del node.literal_type
        #
        #    Instead of reassigning below.
        if hasattr(node, "literal_type") and node.literal_type:
            node.literal_type = lower_type(node.literal_type)
            # Now literal_type is something like "i32_string" or "f64"

    # ------------------------------------------------------------------------
    # B) Lower node.inferred_type for any node type (including literals)
    # ------------------------------------------------------------------------
    inferred = getattr(node, "inferred_type", None)
    if inferred is not None:
        node.inferred_type = lower_type(inferred)

    # ------------------------------------------------------------------------
    # C) Lower node.type_annotation, if present
    # ------------------------------------------------------------------------
    if hasattr(node, "type_annotation") and node.type_annotation:
        node.type_annotation = lower_type(node.type_annotation)

    # ------------------------------------------------------------------------
    # D) If it's a FunctionDefinition => unify .return_type
    # ------------------------------------------------------------------------
    if node.type == "FunctionDefinition":
        if hasattr(node, "return_type") and node.return_type:
            node.return_type = lower_type(node.return_type)

    # ------------------------------------------------------------------------
    # Special node-type handling
    # ------------------------------------------------------------------------

    # (E1) ConversionExpression => from_type, to_type, source_expr
    if node.type == "ConversionExpression":
        from_t = getattr(node, "from_type", None)
        to_t   = getattr(node, "to_type", None)
        if from_t:
            node.from_type = lower_type(from_t)
        if to_t:
            node.to_type = lower_type(to_t)
        if getattr(node, "source_expr", None):
            lower_node(node.source_expr)

    # (E2) FnExpression => lower 'name' if it's a nested dict, plus arguments
    if node.type == "FnExpression":
        maybe_name_node = getattr(node, "name", None)
        if maybe_name_node and isinstance(maybe_name_node, dict):
            lower_node(maybe_name_node)

        if hasattr(node, "arguments"):
            for arg in node.arguments:
                lower_node(arg)

    # (E3) LetStatement => variable + expression
    if node.type == "LetStatement":
        if getattr(node, "variable", None):
            lower_node(node.variable)
        if getattr(node, "expression", None):
            lower_node(node.expression)

    # (E4) PrintStatement => node.expressions
    if hasattr(node, "expressions"):
        for expr in node.expressions:
            lower_node(expr)

    # (E5) If the node has .body (Program, FunctionDefinition, BlockStatement)
    if hasattr(node, "body") and node.body:
        for child in node.body:
            lower_node(child)

    # (E6) If the node has .params (function parameters)
    if hasattr(node, "params"):
        for p in node.params:
            if getattr(p, "type_annotation", None):
                p.type_annotation = lower_type(p.type_annotation)
            if getattr(p, "inferred_type", None):
                p.inferred_type = lower_type(p.inferred_type)

    # (E7) Single-child expressions: operand / left / right

    if node.type == "AssignmentExpression":
        # If this node itself has an inferred_type, lower it
        inferred_assn = getattr(node, "inferred_type", None)
        if inferred_assn is not None:
            node.inferred_type = lower_type(inferred_assn)

        # Recurse into left side (param name) and right side (value)
        if getattr(node, "left", None):
            lower_node(node.left)
        if getattr(node, "right", None):
            lower_node(node.right)

        return  # skip the generic .operand/.left/.right recursion below

    # If not an AssignmentExpression, handle the generic .operand/.left/.right
    if getattr(node, "operand", None):
        lower_node(node.operand)
    if getattr(node, "left", None):
        lower_node(node.left)
    if getattr(node, "right", None):
        lower_node(node.right)
    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

    # (F) IfStatement => condition, then_body, elseif_clauses, else_body
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

    if node.type == "ReturnStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)

    if node.type == "AssignmentStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)
    # ... Additional expansions go here ...
