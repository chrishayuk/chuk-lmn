# file: lmn/compiler/emitter/wasm/expressions/array_literal_expression_emitter.py
import json
import logging

logger = logging.getLogger(__name__)

class ArrayLiteralExpressionEmitter:
    """
    Emits a textual bracket-literal representation for arrays if 
    we can't or don't want to do a typed numeric array.

    Example usage (untyped arrays):
      node = {
        "type": "ArrayLiteralExpression",
        "inferred_type": "i32_ptr",  # some fallback
        "elements": [
          { "type": "LiteralExpression", "value": "red", ... },
          { "type": "LiteralExpression", "value": 3.14, ... }
        ]
      }
    Produces data segment storing '["red",3.14]' plus a null terminator,
    and returns i32 pointer => call $print_string.
    """

    def __init__(self, controller):
        """
        :param controller: your WasmEmitter or codegen context, providing:
         - controller._add_data_segment(text): returns memory offset
         - controller.emit_expression(expr, out_lines): optional sub-expr usage
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Builds bracket-literal text from the array's elements,
        stores it in a data segment, then does `i32.const <offset>`.
        """
        logger.debug("ArrayLiteralExpressionEmitter => fallback text array, node=%r", node)

        elements = node.get("elements", [])
        if not elements:
            array_str = "[]"
        else:
            array_str = self._serialize_elements(elements)

        offset = self.controller._add_data_segment(array_str)
        out_lines.append(f"  i32.const {offset}")

    def _serialize_elements(self, elements):
        """
        Convert each element to a JSON-like string. 
        E.g. [1,"foo",3.14]
        """
        serialized_values = []
        for elem in elements:
            if elem["type"] == "LiteralExpression":
                val = elem.get("value")
                inf_type = elem.get("inferred_type")

                # If it's a string literal
                if isinstance(val, str) and (inf_type == "string"):
                    serialized_values.append(val)

                # If it's numeric
                elif isinstance(val, (int, float)):
                    serialized_values.append(val)

                else:
                    # unknown literal => fallback
                    serialized_values.append(str(val))
            else:
                # For non-literal or more complex subexpr
                serialized_values.append(f"<expr:{elem['type']}>")

        # Convert to JSON-ish array, e.g. ["red", 3.14]
        return json.dumps(serialized_values)
