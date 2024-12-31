# file: lmn/compiler/emitter/wasm/expressions/array_int_literal_expression_emitter.py

import struct
import logging
from .expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)

class IntArrayLiteralEmitter:
    """
    Builds a memory block for 'int[]' arrays in WebAssembly:
      - 4 bytes for the array length (i32),
      - Followed by 'length' elements, each 4 bytes (i32, little-endian).

    Then places that block in a data segment, and emits `i32.const <offset>`
    so the Wasm code sees that pointer on the stack.
    """

    def __init__(self, controller):
        """
        :param controller: your WasmEmitter or codegen context:
          - controller.current_data_offset (int)
          - controller.data_segments (list of (offset, bytes))
          - etc.
        """
        self.controller = controller

    def emit_int_array(self, node, out_lines):
        """
        Emits an int array to the data segments and appends the pointer to out_lines.
        """
        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(f"Emitting int[] of length {length} for node={node}")

        # 1) Build raw bytes => 4 bytes for array length + each i32
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)  # i32 length

        # 2) Evaluate each element, store as i32
        for elem in elements:
            val = ExpressionEvaluator.evaluate_expression(elem, expected_type='int')
            # Optionally, clamp or range-check
            # if val < -2**31 or val > 2**31 - 1:
            #     logger.warning(f"Value {val} out of 32-bit range; clamping to 0.")
            #     val = 0

            data_bytes += struct.pack("<i", val)

        # 3) Append to data segments
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            f"int[] => offset={offset}, size={len(data_bytes)} bytes, elements={length}"
        )

        # 4) Emit instructions => push that offset on the stack
        out_lines.append(f"  i32.const {offset}")
