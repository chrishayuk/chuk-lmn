# file: lmn/compiler/emitter/wasm/expressions/literal_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class LiteralExpressionEmitter:
    def __init__(self, controller):
        """
        'controller' references the main WasmEmitter or similar.
        We assume `controller._add_data_segment(text)` is available
        and returns an integer offset in memory.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node:
          {
            "type": "LiteralExpression",
            "value": 2.718,
            "inferred_type": "f32"
          }
        or a string:
          {
            "type": "LiteralExpression",
            "value": "Hello\n🌍 \"Earth\"!",
            "inferred_type": "i32_string"
          }
        or arbitrary pointer-literal:
          {
            "type": "LiteralExpression",
            "value": "[1,2,3]",
            "inferred_type": "i32_ptr"
          }
        """
        inferred_t = node.get("inferred_type", "")
        literal_val = str(node["value"])

        logger.debug(
            "LiteralExpressionEmitter.emit() -> literal_value=%r, inferred_type=%r",
            literal_val, inferred_t
        )

        # ----------------------------
        # (A) Numeric recognized types
        # ----------------------------
        if inferred_t in ("i32", "i64", "f32", "f64"):
            logger.debug(
                "LiteralExpressionEmitter: recognized numeric type=%s for literal='%s'",
                inferred_t, literal_val
            )
            self._emit_numeric_literal(inferred_t, literal_val, out_lines)

        # ----------------------------
        # (B) Pointer/string recognized types
        # ----------------------------
        elif inferred_t in (
            "i32_string",      # typical "string pointer"
            "i32_ptr",
            "i32_json",
            "i32_string_array",
            "i32_json_array"
        ):
            logger.debug(
                "LiteralExpressionEmitter: recognized pointer/string type='%s' => store in data segment",
                inferred_t
            )
            offset = self.controller._add_data_segment(literal_val)
            logger.debug(
                "LiteralExpressionEmitter: data_segment offset=%d for literal='%s'",
                offset, literal_val
            )
            out_lines.append(f"  i32.const {offset}")

        # ----------------------------
        # (C) Fallback: unrecognized
        #     => Try to interpret as numeric via _infer_wasm_type
        # ----------------------------
        else:
            logger.debug(
                "LiteralExpressionEmitter: unrecognized or missing 'inferred_type' => fallback to numeric detection for '%s'",
                literal_val
            )
            num_type = self._infer_wasm_type(literal_val)
            self._emit_numeric_literal(num_type, literal_val, out_lines)

    def _emit_numeric_literal(self, wasm_type, literal_value, out_lines):
        """
        Emit instructions for numeric WASM types: i32, i64, f32, f64.
        """
        logger.debug(
            "LiteralExpressionEmitter: _emit_numeric_literal => wasm_type=%r, literal_value=%r",
            wasm_type, literal_value
        )

        if wasm_type == "i32":
            out_lines.append(f"  i32.const {literal_value}")
        elif wasm_type == "i64":
            out_lines.append(f"  i64.const {literal_value}")
        elif wasm_type == "f32":
            out_lines.append(f"  f32.const {literal_value}")
        elif wasm_type == "f64":
            out_lines.append(f"  f64.const {literal_value}")
        else:
            raise ValueError(
                f"Unsupported numeric type {wasm_type} for literal '{literal_value}'"
            )

    def _infer_wasm_type(self, literal_str):
        """
        Naive fallback if there's no or unknown 'inferred_type'.
        We'll do a basic numeric detection:
          - If there's '.' or 'e' => treat as float => 'f64'
          - If trailing 'f' => 'f32'
          - Else parse as int => 'i32' or 'i64' depending on range
          - If parse fails => fallback to 'f64'
        """
        logger.debug("_infer_wasm_type() => analyzing literal_str='%s'", literal_str)
        
        # quick float check
        is_float_syntax = ('.' in literal_str) or ('e' in literal_str.lower())
        if is_float_syntax:
            # Check for trailing 'f' => treat as f32
            if literal_str.lower().endswith('f'):
                logger.debug("Literal '%s' => treat as f32 due to trailing 'f'", literal_str)
                return 'f32'
            else:
                logger.debug("Literal '%s' => treat as f64 (float-syntax, no 'f')", literal_str)
                return 'f64'
        else:
            # It's integer-like
            try:
                val = int(literal_str, 0)
                logger.debug("Parsed literal '%s' => int value=%s", literal_str, val)
            except ValueError:
                logger.debug("Literal '%s' => parse error => fallback f64", literal_str)
                return 'f64'  # fallback

            if -2147483648 <= val <= 2147483647:
                logger.debug("Literal '%s' => within 32-bit signed range => 'i32'", literal_str)
                return 'i32'
            else:
                logger.debug("Literal '%s' => out of 32-bit range => 'i64'", literal_str)
                return 'i64'
