# file: lmn/compiler/emitter/wasm/expressions/literal_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class LiteralExpressionEmitter:
    def __init__(self, controller):
        """
        'controller' references the main WasmEmitter or similar.
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
        """
        inferred_t = node.get("inferred_type")
        literal_value = str(node["value"]).strip()

        logger.debug(
            "LiteralExpressionEmitter.emit() -> literal_value=%r, inferred_type=%s",
            literal_value, inferred_t
        )

        # If we have a recognized inferred_t in ('i32', 'i64', 'f32', 'f64'), use it
        if inferred_t in ("i32", "i64", "f32", "f64"):
            logger.debug("Using provided inferred_type=%s for literal='%s'", inferred_t, literal_value)
            if inferred_t == "i32":
                line = f"  i32.const {literal_value}"
            elif inferred_t == "i64":
                line = f"  i64.const {literal_value}"
            elif inferred_t == "f32":
                line = f"  f32.const {literal_value}"
            else:  # "f64"
                line = f"  f64.const {literal_value}"
            logger.debug("Emitting => %s", line.strip())
            out_lines.append(line)
        else:
            # Fallback if no 'inferred_type'
            logger.debug(
                "No recognized 'inferred_type' for literal='%s'; falling back to _infer_wasm_type()",
                literal_value
            )
            num_type = self._infer_wasm_type(literal_value)
            if num_type == 'i32':
                line = f'  i32.const {literal_value}'
            elif num_type == 'i64':
                line = f'  i64.const {literal_value}'
            elif num_type == 'f32':
                line = f'  f32.const {literal_value}'
            elif num_type == 'f64':
                line = f'  f64.const {literal_value}'
            else:
                raise ValueError(f"Unsupported numeric type for literal: {literal_value}")

            logger.debug(
                "Fallback type -> %s, Emitting => %s",
                num_type, line.strip()
            )
            out_lines.append(line)

    def _infer_wasm_type(self, literal_str):
        """
        Naive fallback if there's no 'inferred_type'.
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
