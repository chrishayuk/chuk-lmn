import json
import logging

logger = logging.getLogger(__name__)

class ArrayLiteralExpressionEmitter:
    """
    Emits a Wasm-friendly pointer for an ArrayLiteralExpression by
    creating a static string representation (e.g., JSON) and putting it
    in a data segment. Then pushes that pointer (i32.const <offset>)
    onto the stack.

    If you need a richer approach (like truly storing each element in
    memory and referencing them), you can expand this logic to create
    a real array data structure. But this snippet suffices for printing
    or basic debugging.
    """

    def __init__(self, controller):
        """
        :param controller: typically your main WasmEmitter or codegen context,
                           which provides:
          - controller._add_data_segment(text) -> offset
            returns the memory offset where 'text' is stored
          - controller.emit_expression(expr, out_lines)
            if you want to recursively emit child expressions
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node structure:
        {
          "type": "ArrayLiteralExpression",
          "inferred_type": "i32_ptr",
          "elements": [
            {
              "type": "LiteralExpression",
              "value": "red",
              "inferred_type": "string"
            },
            {
              "type": "LiteralExpression",
              "value": "green",
              "inferred_type": "string"
            },
            ...
          ]
        }

        We'll build a string like '["red","green","blue"]' or "[red, green, ...]",
        store it in a data segment, and push the pointer (i32.const offset).
        """
        logger.debug("ArrayLiteralExpressionEmitter.emit() -> node=%r", node)

        elements = node.get("elements", [])
        if not elements:
            # For an empty array, just store "[]"
            array_str = "[]"
        else:
            array_str = self._serialize_elements(elements)

        # Add the resulting string to a data segment => get offset
        offset = self.controller._add_data_segment(array_str)

        # Emit an instruction to put that pointer on the stack
        out_lines.append(f"  i32.const {offset}")

    def _serialize_elements(self, elements):
        """
        Build a textual representation (e.g. JSON) from the array's elements.
        If an element is a literal string or number, we store it directly;
        otherwise, we convert the node to a string for fallback.
        """
        serialized_values = []
        for elem in elements:
            if elem["type"] == "LiteralExpression":
                val = elem.get("value")
                inf_type = elem.get("inferred_type")

                # 1) If it's a string literal
                if isinstance(val, str) and (inf_type == "string"):
                    serialized_values.append(val)

                # 2) If it's numeric (int/float)
                elif isinstance(val, (int, float)):
                    serialized_values.append(val)

                else:
                    # fallback to str(...) for unknown literal
                    serialized_values.append(str(val))

            else:
                # For non-literal elements, store a fallback
                # or call self.controller.emit_expression(...) if you want deeper logic
                serialized_values.append(f"<expr:{elem['type']}>")

        # Convert the Python list to a JSON array string, e.g. ["red","green","blue"]
        return json.dumps(serialized_values)
