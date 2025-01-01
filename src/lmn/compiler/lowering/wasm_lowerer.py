# file: lmn/compiler/lowering/wasm_lowerer.py

from typing import Optional, Dict, Any

##############################################################################
# 1) Mappings from language-level types to WASM-level (or pointer-level) types
##############################################################################

# For single (non-array) scalars:
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

# For typed arrays or generic "array":
LANG_TO_WASM_ARRAYS: Dict[str, str] = {
    "int[]":      "i32_ptr",
    "long[]":     "i64_ptr",
    "float[]":    "f32_ptr",
    "double[]":   "f64_ptr",

    # Strings in arrays:
    "string[]":   "i32_string_array",

    # JSON arrays:
    "json[]":     "i32_json_array",

    # If you have a generic "array" type:
    "array":      "i32_ptr"
}


##############################################################################
# 2) The function to map a single type name to its lowered WASM form
##############################################################################

def lower_type(lang_type: Optional[str]) -> str:
    """
    Convert a language-level type string (e.g. "int[]", "json", "string") 
    to a WASM-level type (e.g. "i32_ptr", "i32_json", "i32_string").

    If unknown, defaults to "i32".
    """
    if not lang_type:
        return "i32"  # If no type is provided, default to i32

    # 1. If the entire type matches something in the arrays map:
    if lang_type in LANG_TO_WASM_ARRAYS:
        return LANG_TO_WASM_ARRAYS[lang_type]

    # 2. If the entire type matches something in the scalars map:
    if lang_type in LANG_TO_WASM_SCALARS:
        return LANG_TO_WASM_SCALARS[lang_type]

    # 3. If it ends with "[]", but wasn't in our array map explicitly:
    if lang_type.endswith("[]"):
        base_type = lang_type[:-2]  # e.g. "string[]" => "string"
        # If base_type is recognized as a scalar, produce a pointer form:
        if base_type in LANG_TO_WASM_SCALARS:
            # For demonstration, let's unify arrays to `_ptr` unless 
            # we want a specialized name:
            if base_type == "string":
                return "i32_string_array"
            elif base_type == "json":
                return "i32_json_array"
            else:
                # e.g., base_type == "int" => "i32", so => "i32_ptr"
                return LANG_TO_WASM_SCALARS[base_type] + "_ptr"
        else:
            # fallback: unknown array => i32_ptr
            return "i32_ptr"

    # 4. If nothing matches, fallback to i32
    return "i32"


##############################################################################
# 3) The main lowering entry point for a Program node
##############################################################################

def lower_program_to_wasm_types(program_node: Any) -> None:
    """
    Called on the top-level 'Program' node to recursively lower every statement.

    :param program_node: The AST node representing the entire program.
                        Typically it has a .body list of statements.
    """
    # We assume program_node.body is a list of top-level statements/functions
    for stmt in program_node.body:
        lower_node(stmt)


##############################################################################
# 4) Recursively lower a single AST node
##############################################################################

def lower_node(node: Any) -> None:
    """
    Convert node.inferred_type / node.type_annotation to WASM-level strings,
    then recurse into child nodes (expressions, body, etc.).
    """

    # 1) Lower the node's own inferred_type
    inferred = getattr(node, "inferred_type", None)
    if inferred is not None:
        node.inferred_type = lower_type(inferred)

    # 2) Lower the node's type_annotation, if present
    if hasattr(node, "type_annotation") and node.type_annotation:
        node.type_annotation = lower_type(node.type_annotation)

    # 3) Recurse into child nodes / statements / expressions

    # If it's a LetStatement => variable + expression
    if node.type == "LetStatement":
        if getattr(node, "variable", None):
            lower_node(node.variable)
        if getattr(node, "expression", None):
            lower_node(node.expression)

    # PrintStatement => node.expressions
    if hasattr(node, "expressions"):
        for expr in node.expressions:
            lower_node(expr)

    # If there's a .body (e.g. Program, BlockStatement, etc.)
    if hasattr(node, "body") and node.body:
        for child in node.body:
            lower_node(child)

    # If there's .params (e.g. function parameters)
    if hasattr(node, "params"):
        for p in node.params:
            if p.type_annotation:
                p.type_annotation = lower_type(p.type_annotation)

    # If there's a single child expression (like x.left, x.right, x.operand)
    if getattr(node, "operand", None):
        lower_node(node.operand)

    if getattr(node, "left", None):
        lower_node(node.left)

    if getattr(node, "right", None):
        lower_node(node.right)

    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

    # If it's an IfStatement, WhileStatement, etc., handle .condition, .then_body, etc.
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

    # ReturnStatement => node.expression
    if node.type == "ReturnStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)

    # AssignmentStatement => x = expr
    if node.type == "AssignmentStatement":
        if getattr(node, "expression", None):
            lower_node(node.expression)

    # That covers the typical statements. 
    # Expand as needed for your language's other node types.
