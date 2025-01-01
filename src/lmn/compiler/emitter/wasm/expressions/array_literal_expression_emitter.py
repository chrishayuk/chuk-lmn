# file: lmn/compiler/emitter/wasm/expressions/array_literal_expression_emitter.py

import json
import logging

logger = logging.getLogger(__name__)

class ArrayLiteralExpressionEmitter:
    """
    Emits a textual bracket-literal representation for arrays if
    we can't or don't want to do a specialized typed array emission.

    Example usage (mixed/untyped arrays):
      node = {
        "type": "ArrayLiteralExpression",
        "inferred_type": "i32_ptr",  # fallback pointer type
        "elements": [
          { "type": "LiteralExpression", "value": "red", "inferred_type": "i32_string", ...},
          { "type": "LiteralExpression", "value": 3.14, "inferred_type": "f64", ...}
        ]
      }
    Produces a data segment storing something like ["red",3.14] plus a null terminator,
    and pushes i32 offset => can be printed with `call $print_string`.
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
        # push the pointer (i32) to the data on the stack
        out_lines.append(f"  i32.const {offset}")

    def _serialize_elements(self, elements):
        """
        Convert each element to a JSON-like string. E.g. [1,"foo",3.14]
        Based on the 'inferred_type' of each literal, we handle i32_string vs. numeric, etc.
        """
        serialized_values = []
        for elem in elements:
            if elem["type"] != "LiteralExpression":
                # Non-literal or complex expressions => fallback
                serialized_values.append(f"<expr:{elem['type']}>")
                continue

            val = elem.get("value")
            inf_type = elem.get("inferred_type", "")

            # If it's a lowered string => i32_string
            if isinstance(val, str) and inf_type == "i32_string":
                serialized_values.append(val)

            # If it's numeric (e.g., i32, i64, f32, f64)
            elif inf_type in ("i32", "i64", "f32", "f64"):
                # val might be an int or float
                serialized_values.append(val)

            else:
                # unknown literal => fallback to string representation
                serialized_values.append(str(val))

        # Convert to JSON-ish array, e.g. ["red",3.14]
        return json.dumps(serialized_values)
