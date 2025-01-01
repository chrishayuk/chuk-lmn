# file: lmn/compiler/emitter/wasm/expressions/array_float_literal_expression_emitter.py

import struct
import logging
from .expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)

class FloatArrayLiteralEmitter:
    """
    Builds a memory block for arrays of 32-bit floats.
    We assume the lowered type is "f32_ptr".

    Layout in memory:
      - 4 bytes for array length (i32)
      - 'length' elements, each 4 bytes (f32, little-endian)

    We place this block in a data segment, returning an i32 pointer to that block.
    """

    def __init__(self, controller):
        """
        :param controller: your WasmEmitter/codegen context:
         - controller.current_data_offset (int)
         - controller.data_segments (list of (offset, bytes))
         - optionally controller.emit_expression(...) if nested calls are needed
        """
        self.controller = controller

    def emit_float_array(self, node, out_lines):
        """
        Example node:
        {
          "type": "ArrayLiteralExpression",
          "inferred_type": "f32_ptr",
          "elements": [
            { "type": "LiteralExpression", "value": 1.0, ... },
            ...
          ]
        }

        We'll build a memory block:
            <length : i32> <elem0 : f32> <elem1 : f32> ...
        Then store them in a data segment. We'll emit `i32.const <offset>` 
        so the pointer is pushed onto the stack.
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "f32_ptr":
            raise ValueError(f"FloatArrayLiteralEmitter: Expected 'f32_ptr', got '{inferred_type}'")

        elements = node.get("elements", [])
        length = len(elements)
        logger.debug(f"Emitting float[] of length {length} for node={node}")

        # 1) Build raw bytes => first 4 bytes => length (i32)
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)

        # 2) Each element => 4 bytes (f32) in little-endian
        for elem in elements:
            val = ExpressionEvaluator.evaluate_expression(elem, expected_type='float')
            # You may clamp or handle special float cases:
            # val = ExpressionEvaluator.clamp_value(val, 'float')

            try:
                packed_val = struct.pack("<f", val)
            except struct.error as e:
                logger.warning(f"Error packing value {val} as f32: {e}; defaulting to 0.0")
                packed_val = struct.pack("<f", 0.0)

            data_bytes += packed_val

        # 3) Add to data segments
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            "f32_ptr memory block => offset=%d, size=%d bytes, elements=%d",
            offset, len(data_bytes), length
        )

        # 4) Push the offset (pointer) as i32 onto the stack
        out_lines.append(f"  i32.const {offset}")
        logger.debug(f"Emitted i32.const {offset}")
