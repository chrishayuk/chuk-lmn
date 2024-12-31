# file: lmn/compiler/emitter/wasm/expressions/array_long_literal_expression_emitter.py

import struct
import logging
from .expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)

class LongArrayLiteralEmitter:
    """
    Emits a Wasm-friendly memory block for `long[]` arrays (64-bit signed integers).
    Layout:
      - 4 bytes for the array length (i32)
      - 'length' elements, each 8 bytes (i64, little-endian)

    Then places the data block into a data segment, and emits 'i32.const <offset>'
    so the code can push that pointer on the stack.
    """

    def __init__(self, controller):
        """
        :param controller: your WasmEmitter or codegen context:
          - controller.current_data_offset (int)
          - controller.data_segments (list of (offset, bytes))
          - etc.
        """
        self.controller = controller

    def emit_long_array(self, node, out_lines):
        """
        Emits a long array to the data segments and appends the pointer to out_lines.
        """
        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(f"Emitting long[] of length {length} for node={node}")

        # 1) Build raw bytes => 4 bytes for length + 8 bytes * number_of_elements
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)  # i32: array length

        # 2) For each element => 8-byte i64
        for elem in elements:
            val = ExpressionEvaluator.evaluate_expression(elem, expected_type='long')
            # Optionally, clamp or check if val is in [-2**63, 2**63-1]
            data_bytes += struct.pack("<q", val)

        # 3) Insert into data segments
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            f"long[] => offset={offset}, size={len(data_bytes)} bytes, elements={length}"
        )

        # 4) i32.const <offset> => pointer on the stack
        out_lines.append(f"  i32.const {offset}")
