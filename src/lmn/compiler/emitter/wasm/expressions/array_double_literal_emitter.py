# file: lmn/compiler/emitter/wasm/expressions/array_double_literal_expression_emitter.py

import struct
import logging
from .expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)

class DoubleArrayLiteralEmitter:
    """
    Builds a memory block for arrays of 64-bit floats.
    We assume the lowered type is "f64_ptr".
    
    Memory layout:
      - 4 bytes for array length (i32)
      - 'length' elements, each 8 bytes (f64, little-endian)

    The block is stored in a data segment, returning an i32 pointer to that block.
    """

    def __init__(self, controller):
        """
        :param controller: the WasmEmitter or codegen context providing:
         - controller.current_data_offset: next free memory offset (int)
         - controller.data_segments: list of (offset, bytes)
         - possibly controller.emit_expression(expr, out_lines) if needed
        """
        self.controller = controller

    def emit_double_array(self, node, out_lines):
        """
        Example node:
        {
          "type": "ArrayLiteralExpression",
          "inferred_type": "f64_ptr",
          "elements": [
            { "type": "LiteralExpression", "value": 1.0, ... },
            ...
          ]
        }

        We'll build a memory block:
            <length : i32> <elem0 : f64> <elem1 : f64> ...
        Then store them in a data segment. We'll emit `i32.const <offset>`
        so the pointer is on the stack.
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "f64_ptr":
            raise ValueError(f"DoubleArrayLiteralEmitter: Expected 'f64_ptr', got '{inferred_type}'")

        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(f"Emitting double array (f64_ptr) of length {length} for node={node}")

        # 1) Build raw bytes: first 4 bytes => array length (i32)
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)

        # 2) Pack each element as 64-bit float (f64, little-endian)
        for elem in elements:
            val = ExpressionEvaluator.evaluate_expression(elem, expected_type='double')
            # You might clamp or handle special double cases here
            # val = ExpressionEvaluator.clamp_value(val, 'double')

            try:
                packed_val = struct.pack("<d", val)
            except struct.error as e:
                logger.warning(f"Error packing value {val} as f64: {e}; defaulting to 0.0")
                packed_val = struct.pack("<d", 0.0)

            data_bytes += packed_val

        # 3) Store in data segment => get an offset
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            "f64_ptr memory block => offset=%d, size=%d bytes, elements=%d",
            offset, len(data_bytes), length
        )

        # 4) Emit instructions => push offset as i32
        out_lines.append(f"  i32.const {offset}")
        logger.debug(f"Emitted i32.const {offset}")
