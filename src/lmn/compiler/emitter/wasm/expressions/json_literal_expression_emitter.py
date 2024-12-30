# file: lmn/compiler/emitter/wasm/expressions/json_literal_expression_emitter.py
import json
import logging

# logger
logger = logging.getLogger(__name__)

class JsonLiteralExpressionEmitter:
    def __init__(self, controller):
        """
        'controller' is typically your main WasmEmitter or a context with:
          - controller._add_data_segment(text) -> offset
        that returns an int offset in linear memory where 'text' was stored.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node:
          {
            "type": "JsonLiteralExpression",
            "inferred_type": "i32_json",
            "value": {
              "name": "Alice",
              "age": 42
            }
          }

        We'll serialize node["value"] (a dict or list) to JSON text, place
        it in a data segment, and emit `i32.const <offset>`.
        """
        logger.debug("JsonLiteralExpressionEmitter.emit() -> node=%r", node)

        # 1) Convert the Python dict/list to a JSON string
        raw_obj = node["value"]        # e.g. {"name":"Alice","age":42}
        json_str = json.dumps(raw_obj) # => '{"name":"Alice","age":42}'

        # 2) Store this string (plus a null terminator) in the data segment
        offset = self.controller._add_data_segment(json_str)

        # 3) Emit the instruction that pushes that offset into i32
        out_lines.append(f"  i32.const {offset}")
