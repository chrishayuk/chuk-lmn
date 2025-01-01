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
        literal_value = str(node["value"]).strip()

        logger.debug(
            "LiteralExpressionEmitter.emit() -> literal_value=%r, inferred_type=%s",
            literal_value, inferred_t
        )

        # (A) If it's a recognized numeric type => emit numeric
        if inferred_t in ("i32", "i64", "f32", "f64"):
            logger.debug(
                "Using provided numeric inferred_type=%s for literal='%s'",
                inferred_t, literal_value
            )
            self._emit_numeric_literal(inferred_t, literal_value, out_lines)

        # (B) If it's a recognized pointer/string type => store in data segment
        elif inferred_t in ("i32_string", "i32_ptr", "i32_json", "i32_string_array", "i32_json_array"):
            logger.debug("Non-numeric literal => store in data segment => push pointer offset")
            offset = self.controller._add_data_segment(literal_value)
            out_lines.append(f"  i32.const {offset}")

        else:
            # (C) No recognized or missing 'inferred_type' => fallback numeric guess
            logger.debug(
                "No recognized 'inferred_type' for literal='%s'; falling back to _infer_wasm_type()",
                literal_value
            )
            num_type = self._infer_wasm_type(literal_value)
            self._emit_numeric_literal(num_type, literal_value, out_lines)

    def _emit_numeric_literal(self, wasm_type, literal_value, out_lines):
        """
        Emit instructions for numeric WASM types: i32, i64, f32, f64.
        """
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
        Naive fallback if there's no 'inferred_type'.
        We do numeric detection: if there's '.' or 'e' => float => f64,
        else parse as int => i32 or i64 range. Otherwise fallback to f64.
        """
        logger.debug("_infer_wasm_type() => analyzing literal_str='%s'", literal_str)
        is_float_syntax = ('.' in literal_str) or ('e' in literal_str.lower())
        if is_float_syntax:
            # If there's a trailing 'f' => treat as f32
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
                logger.debug("Literal '%s' => fallback f64", literal_str)
                return 'f64'  # fallback

            if -2147483648 <= val <= 2147483647:
                logger.debug("Literal '%s' => in 32-bit range => 'i32'", literal_str)
                return 'i32'
            else:
                logger.debug("Literal '%s' => out of 32-bit range => 'i64'", literal_str)
                return 'i64'
