# file: lmn/compiler/emitter/wasm/expressions/conversion_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class ConversionExpressionEmitter:
    """
    Handles explicit type conversions between the new lowered WASM types:
      - i32 <-> i64
      - f32 <-> f64
      - i32_string -> i32 (string pointer parse)
      etc.
    """

    def __init__(self, controller):
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node:
          {
            "type": "ConversionExpression",
            "from_type": "i32_string",
            "to_type": "i32",
            "source_expr": {...another AST node...},
            "inferred_type": "i32"
          }
        We'll:
          1) Emit code for source_expr (which leaves an i32 pointer on the stack)
          2) Insert the correct WASM op, e.g. call $parse_string_to_i32
        """

        source_expr = node["source_expr"]

        # 1) Emit the source expression => leaves pointer or numeric on the stack
        self.controller.emit_expression(source_expr, out_lines)

        # 2) Determine from/to
        from_t = node["from_type"]
        to_t   = node["to_type"]

        logger.debug(
            "ConversionExpressionEmitter: from_type=%s -> to_type=%s",
            from_t, to_t
        )

        # 3) Insert the appropriate WASM conversion op or parse call
        if from_t == "f32" and to_t == "f64":
            out_lines.append("  f64.promote_f32")

        elif from_t == "f64" and to_t == "f32":
            out_lines.append("  f32.demote_f64")

        elif from_t == "i32" and to_t == "i64":
            out_lines.append("  i64.extend_i32_s")

        elif from_t == "i64" and to_t == "i32":
            out_lines.append("  i32.wrap_i64")

        # === NEW CODE: handle string->int parse ===
        elif from_t == "i32_string" and to_t == "i32":
            # Insert your parse call:
            # We'll assume you have: (import "env" "parse_string_to_i32" (func $parse_string_to_i32 (param i32) (result i32)))
            out_lines.append("  call $parse_string_to_i32")

        elif from_t == "i32_string" and to_t == "i64":
            out_lines.append("  call $parse_string_to_i64")

        else:
            # Fallback: warn or throw
            logger.warning(
                "Unsupported conversion from '%s' to '%s' in ConversionExpressionEmitter. "
                "No op emitted.",
                from_t, to_t
            )
            # raise ValueError(f"Unsupported conversion: {from_t} -> {to_t}")
