# file: lmn/compiler/emitter/wasm/expressions/json_literal_expression_emitter.py
import json
import logging

logger = logging.getLogger(__name__)

class JsonLiteralExpressionEmitter:
    """
    Serializes node["value"] (a Python dict or list) into JSON text, places
    that text in the data segment, and emits `i32.const <offset>`.
    Accepts both "i32_json" (object) and "i32_json_array" (array).
    """

    def __init__(self, controller):
        """
        :param controller: Typically your main WasmEmitter or context with:
           - controller._add_data_segment(text) -> offset
           - controller.data_segments, controller.current_data_offset, etc.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node for a single JSON object:
          {
            "type": "JsonLiteralExpression",
            "inferred_type": "i32_json",
            "value": { "hello": "world" }
          }

        Example node for an array of JSON objects:
          {
            "type": "JsonLiteralExpression",
            "inferred_type": "i32_json_array",
            "value": [
              { "foo": "bar" },
              { "foo": "baz" }
            ]
          }

        1) Check that 'inferred_type' is in ("i32_json", "i32_json_array")
        2) `json.dumps(...)` the node["value"]
        3) Store the result in the data segment
        4) Emit `i32.const <offset>`
        """
        logger.debug("JsonLiteralExpressionEmitter.emit() -> node=%r", node)

        inferred_type = node.get("inferred_type", "")
        # Accept both single JSON and JSON array pointers
        if inferred_type not in ("i32_json", "i32_json_array"):
            raise ValueError(
                f"JsonLiteralExpressionEmitter: Expected 'i32_json' or 'i32_json_array', got '{inferred_type}'"
            )

        # Convert the Python dict/list to JSON text
        raw_obj = node.get("value", {})
        json_str = json.dumps(raw_obj)  # e.g. '[{"foo": "bar"}]' or '{"foo":"bar"}'

        # Store this JSON text (plus null terminator) in the data segment
        offset = self.controller._add_data_segment(json_str)
        logger.debug(
            "JsonLiteralExpressionEmitter: Stored JSON at offset %d: %s", 
            offset, json_str
        )

        # Emit `i32.const <offset>` => pointer onto the stack
        out_lines.append(f"  i32.const {offset}")
        logger.debug(f"JsonLiteralExpressionEmitter: Emitted 'i32.const {offset}'")
