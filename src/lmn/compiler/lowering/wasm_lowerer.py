# file: lmn/compiler/lowering/wasm_lowerer.py

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

##############################################################################
# 1) Mappings from language-level types to WASM-level (or pointer-level) types
##############################################################################

LANG_TO_WASM_SCALARS: Dict[str, str] = {
    "int":         "i32",
    "long":        "i64",
    "float":       "f32",
    "double":      "f64",
    "f64":         "f64",        # Some DSLs explicitly say "f64" for double-precision
    "string":      "i32_string",
    "i32_string":  "i32_string",
    "json":        "i32_json",
}

LANG_TO_WASM_ARRAYS: Dict[str, str] = {
    # Standard arrays
    "int[]":       "i32_ptr",
    "long[]":      "i64_ptr",
    "float[]":     "f32_ptr",
    "double[]":    "f64_ptr",
    "string[]":    "i32_string_array",
    "json[]":      "i32_json_array",

    # If your code also uses "i32_string_array" directly:
    # Force it to remain i32_string_array (rather than fallback to i32).
    "i32_string_array": "i32_string_array",

    # If the DSL uses "array" as a general untyped array:
    "array":       "i32_ptr",
}


##############################################################################
# 2) Convert a language-level type to WASM-level
##############################################################################

def lower_type(lang_type: Optional[str]) -> str:
    """
    Convert a language-level type string to a WASM-level type.
    e.g. "int[]" => "i32_ptr", "json" => "i32_json", "string" => "i32_string", etc.

    If `lang_type` is not a string (e.g. it's a dict, or None),
    we default to 'i32'.
    """
    if not isinstance(lang_type, str):
        logger.debug("lower_type: lang_type=%r is not a string => default 'i32'", lang_type)
        return "i32"

    # 1) Direct array mapping (e.g. "string[]" => "i32_string_array")
    if lang_type in LANG_TO_WASM_ARRAYS:
        wasm_type = LANG_TO_WASM_ARRAYS[lang_type]
        logger.debug("lower_type: recognized array type '%s' => '%s'", lang_type, wasm_type)
        return wasm_type

    # 2) Direct scalar mapping (e.g. "string" => "i32_string")
    if lang_type in LANG_TO_WASM_SCALARS:
        wasm_type = LANG_TO_WASM_SCALARS[lang_type]
        logger.debug("lower_type: recognized scalar type '%s' => '%s'", lang_type, wasm_type)
        return wasm_type

    # 3) If it ends with "[]", parse T[] => T_ptr
    if lang_type.endswith("[]"):
        base = lang_type[:-2]
        logger.debug("lower_type: detected array suffix in '%s' => base='%s'", lang_type, base)
        if base in LANG_TO_WASM_SCALARS:
            if base == "string":
                logger.debug("lower_type: base='string' => 'i32_string_array'")
                return "i32_string_array"
            elif base == "json":
                logger.debug("lower_type: base='json' => 'i32_json_array'")
                return "i32_json_array"
            else:
                # e.g. "int" => "i32_ptr"
                wasm_base = LANG_TO_WASM_SCALARS[base]
                logger.debug("lower_type: base='%s' => '%s_ptr'", base, wasm_base)
                return wasm_base + "_ptr"
        else:
            logger.debug("lower_type: unknown array base='%s' => default 'i32_ptr'", base)
            return "i32_ptr"

    # 4) Fallback => "i32"
    logger.debug("lower_type: unrecognized lang_type='%s' => default 'i32'", lang_type)
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
    logger.debug("lower_program_to_wasm_types: processing top-level Program node")
    if not program_node:
        logger.debug("lower_program_to_wasm_types: program_node is None => skipping")
        return

    body = getattr(program_node, "body", [])
    logger.debug("lower_program_to_wasm_types: found %d top-level statements", len(body))
    for stmt in body:
        lower_node(stmt)


def lower_node(node: Any) -> None:
    """
    Recursively update node.inferred_type, node.type_annotation, node.return_type,
    and node.literal_type to WASM-level strings. Then descend into children.
    """
    if not node:
        logger.debug("lower_node: node is None => skipping")
        return

    node_type = getattr(node, "type", None)
    logger.debug("lower_node: visiting node type=%r", node_type)

    # ---------------------------------------------------------
    # (A) Handle BreakStatement or ContinueStatement
    # ---------------------------------------------------------
    if node_type == "BreakStatement":
        node.inferred_type = "void"
        logger.debug("lower_node: BreakStatement => set inferred_type='void'")
        return

    if node_type == "ContinueStatement":
        node.inferred_type = "void"
        logger.debug("lower_node: ContinueStatement => set inferred_type='void'")
        return

    # ------------------ A) If it's a LiteralExpression ------------------
    if node_type == "LiteralExpression":
        # 1) Check existing .inferred_type and .literal_type
        inferred = getattr(node, "inferred_type", None)
        lit_type  = getattr(node, "literal_type", None)

        logger.debug(
            "lower_node(LiteralExpression): inferred=%r, literal_type=%r, value=%r",
            inferred, lit_type, getattr(node, "value", None)
        )

        # If no inferred_type, we try from literal_type
        if inferred is None and lit_type:
            node.inferred_type = lower_type(lit_type)
            logger.debug(
                "lower_node(LiteralExpression): set node.inferred_type from literal_type => %r",
                node.inferred_type
            )

        # If it's a "string" literal, forcibly set i32_string
        if lit_type == "string" or inferred == "string":
            logger.debug(
                "lower_node(LiteralExpression): forcing i32_string for string-literal => was inferred=%r",
                inferred
            )
            node.inferred_type = "i32_string"

        # 2) Also lower the .literal_type => e.g. 'string' => 'i32_string'
        if lit_type:
            lowered_lit = lower_type(lit_type)
            logger.debug("lower_node(LiteralExpression): literal_type=%r => %r", lit_type, lowered_lit)
            node.literal_type = lowered_lit

    # ------------------ A.5) If it's an ArrayLiteralExpression ------------------
    elif node_type == "ArrayLiteralExpression":
        # First, lower this array's own .inferred_type
        array_inferred = getattr(node, "inferred_type", None)
        if array_inferred is not None:
            lowered_array_inferred = lower_type(array_inferred)
            logger.debug(
                "lower_node(ArrayLiteralExpression): node.inferred_type=%r => %r",
                array_inferred, lowered_array_inferred
            )
            node.inferred_type = lowered_array_inferred

        # Then, recursively lower each element in node.elements
        elements = getattr(node, "elements", [])
        logger.debug(
            "lower_node(ArrayLiteralExpression): found %d elements => lowering each",
            len(elements)
        )
        for elem in elements:
            lower_node(elem)

    # ------------------ B) Lower node.inferred_type (if present) ------------------
    inferred_now = getattr(node, "inferred_type", None)
    if inferred_now is not None:
        lowered_inferred = lower_type(inferred_now)
        logger.debug(
            "lower_node: node.inferred_type=%r => lowered=%r",
            inferred_now, lowered_inferred
        )
        node.inferred_type = lowered_inferred

    # ------------------ C) Lower node.type_annotation (if present) ------------------
    if hasattr(node, "type_annotation") and node.type_annotation:
        original_annot = node.type_annotation
        lowered_annot  = lower_type(original_annot)
        logger.debug(
            "lower_node: type_annotation=%r => lowered=%r",
            original_annot, lowered_annot
        )
        node.type_annotation = lowered_annot

    # ------------------ D) If it's a FunctionDefinition => unify .return_type ------------------
    if node_type == "FunctionDefinition":
        return_t = getattr(node, "return_type", None)
        if return_t:
            lowered_ret = lower_type(return_t)
            logger.debug("FunctionDefinition: return_type=%r => %r", return_t, lowered_ret)
            node.return_type = lowered_ret

    # ------------------ E) Additional logic for known node sub-fields ------------------
    if node_type == "ConversionExpression":
        from_t = getattr(node, "from_type", None)
        if from_t:
            new_from = lower_type(from_t)
            logger.debug("ConversionExpression: from_type=%r => %r", from_t, new_from)
            node.from_type = new_from

        to_t = getattr(node, "to_type", None)
        if to_t:
            new_to = lower_type(to_t)
            logger.debug("ConversionExpression: to_type=%r => %r", to_t, new_to)
            node.to_type = new_to

        if getattr(node, "source_expr", None):
            lower_node(node.source_expr)

    if node_type == "FnExpression":
        name_node = getattr(node, "name", None)
        if name_node and isinstance(name_node, dict):
            lower_node(name_node)
        if hasattr(node, "arguments"):
            for arg in node.arguments:
                lower_node(arg)

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

    # If the node has .params => might have type_annotation
    if hasattr(node, "params"):
        for p in node.params:
            if getattr(p, "type_annotation", None):
                p.type_annotation = lower_type(p.type_annotation)
            if getattr(p, "inferred_type", None):
                p.inferred_type = lower_type(p.inferred_type)

    if node_type == "AssignmentExpression":
        if getattr(node, "inferred_type", None):
            node.inferred_type = lower_type(node.inferred_type)
        if getattr(node, "left", None):
            lower_node(node.left)
        if getattr(node, "right", None):
            lower_node(node.right)
        return

    # fallback for operand/left/right/arguments
    if getattr(node, "operand", None):
        lower_node(node.operand)
    if getattr(node, "left", None):
        lower_node(node.left)
    if getattr(node, "right", None):
        lower_node(node.right)
    if hasattr(node, "arguments"):
        for arg in node.arguments:
            lower_node(arg)

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
