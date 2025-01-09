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
        Builds a bracket-literal text from the array's elements,
        stores it in a data segment, then does `i32.const <offset>`.
        
        1) Gathers the array elements into a JSON-like string. e.g.: '["foo",3.14]'
        2) Calls `controller._add_data_segment(...)` to store that string, 
           receiving a linear-memory offset (int).
        3) Emits `i32.const <offset>` onto `out_lines` so we have a pointer to the bracket-literal.
        """
        logger.debug("ArrayLiteralExpressionEmitter: emit() called with node=%r", node)

        elements = node.get("elements", [])
        logger.debug("ArrayLiteralExpressionEmitter: array has %d elements", len(elements))

        if not elements:
            # If no elements => "[]"
            array_str = "[]"
            logger.debug("ArrayLiteralExpressionEmitter: No elements => using '[]'")
        else:
            # Otherwise, we do a bracket-literal w/ JSON-like
            array_str = self._serialize_elements(elements)

        logger.debug(
            "ArrayLiteralExpressionEmitter: Final bracket-literal string => %r", 
            array_str
        )

        # store the bracket-literal string in a data segment
        offset = self.controller._add_data_segment(array_str)
        logger.debug(
            "ArrayLiteralExpressionEmitter: Stored bracket-literal at offset %d", 
            offset
        )

        # push the pointer (i32) to that data on the stack
        out_lines.append(f"  i32.const {offset}")
        logger.debug(
            "ArrayLiteralExpressionEmitter: Emitted 'i32.const %d' onto the stack", 
            offset
        )

    def _serialize_elements(self, elements):
        """
        Convert each element to a JSON-like string. e.g. [1,"foo",3.14]
        Based on 'inferred_type', we handle e.g. i32_string vs. numeric, etc.
        
        1) For each element:
           - If not a LiteralExpression => use a placeholder like <expr:FnExpression>.
           - If 'literal_type' = 'string' => treat it as text.
           - If numeric => keep as numeric in the bracket-literal.
           - Otherwise, fallback to str(value).
        2) Return the final JSON-encoded array: '["foo",3.14]'
        """
        logger.debug("ArrayLiteralExpressionEmitter: _serialize_elements called")

        serialized_values = []
        for i, elem in enumerate(elements):
            etype = elem["type"]
            val = elem.get("value")
            inf_type = elem.get("inferred_type", "")

            logger.debug(
                "ArrayLiteralExpressionEmitter: element[%d] => type=%r, inferred_type=%r, value=%r",
                i, etype, inf_type, val
            )

            if etype != "LiteralExpression":
                # Non-literal => fallback placeholder
                placeholder = f"<expr:{etype}>"
                logger.warning(
                    "ArrayLiteralExpressionEmitter: element[%d] is not a literal => using placeholder %r",
                    i, placeholder
                )
                serialized_values.append(placeholder)
                continue

            # If it's a lowered string => i32_string
            if isinstance(val, str) and inf_type == "i32_string":
                logger.debug(
                    "ArrayLiteralExpressionEmitter: element[%d] => recognized as string: %r", 
                    i, val
                )
                serialized_values.append(val)

            # If it's numeric (e.g., i32, i64, f32, f64)
            elif inf_type in ("i32", "i64", "f32", "f64"):
                logger.debug(
                    "ArrayLiteralExpressionEmitter: element[%d] => numeric %r", 
                    i, val
                )
                serialized_values.append(val)

            else:
                # unknown literal => fallback to str(val)
                fallback_str = str(val)
                logger.warning(
                    "ArrayLiteralExpressionEmitter: element[%d] => unknown literal => using string %r",
                    i, fallback_str
                )
                serialized_values.append(fallback_str)

        # Convert to JSON-ish array, e.g. ["red",3.14]
        result = json.dumps(serialized_values)
        logger.debug("ArrayLiteralExpressionEmitter: serialized result => %r", result)
        return result
