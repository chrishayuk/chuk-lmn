# file: lmn/compiler/emitter/wasm/expressions/conversion_expression_emitter.py
import logging

logger = logging.getLogger(__name__)

class ConversionExpressionEmitter:
    """
    Handles explicit type conversions between the new lowered WASM types:
      - i32 <-> i64
      - f32 <-> f64
    Optionally, you could extend to i32->f32 or f64->i32, etc., if needed.
    """

    def __init__(self, controller):
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node:
          {
            "type": "ConversionExpression",
            "from_type": "f32",
            "to_type": "f64",
            "source_expr": {...another AST node...},
            "inferred_type": "f64"
          }

        We'll:
          1) Emit code for source_expr
          2) Insert the correct WASM op, e.g. "f64.promote_f32".
        """
        source_expr = node["source_expr"]

        # 1) Emit the source expression
        self.controller.emit_expression(source_expr, out_lines)

        # 2) Determine from/to WASM types
        from_t = node["from_type"]  # e.g. "f32"
        to_t   = node["to_type"]    # e.g. "f64"

        logger.debug(
            "ConversionExpressionEmitter: from_type=%s -> to_type=%s",
            from_t, to_t
        )

        # 3) Insert appropriate WASM conversion ops
        if from_t == "f32" and to_t == "f64":
            out_lines.append("  f64.promote_f32")

        elif from_t == "f64" and to_t == "f32":
            out_lines.append("  f32.demote_f64")

        elif from_t == "i32" and to_t == "i64":
            out_lines.append("  i64.extend_i32_s")

        elif from_t == "i64" and to_t == "i32":
            out_lines.append("  i32.wrap_i64")

        else:
            logger.warning(
                "Unsupported conversion from '%s' to '%s' in ConversionExpressionEmitter. "
                "No op emitted.",
                from_t, to_t
            )
            # Optionally raise an error here:
            # raise ValueError(f"Unsupported conversion: {from_t} -> {to_t}")
