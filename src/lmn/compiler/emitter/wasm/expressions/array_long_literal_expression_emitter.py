# file: lmn/compiler/emitter/wasm/expressions/array_long_literal_expression_emitter.py

import struct
import logging
from .expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)

class LongArrayLiteralEmitter:
    """
    Emits a Wasm-friendly memory block for arrays of 64-bit signed integers.
    We assume the lowered type is "i64_ptr".
    
    Layout in memory:
      - 4 bytes for the array length (i32)
      - `length` elements, each 8 bytes (i64, little-endian)

    Finally, places the data block into a data segment, then emits:
      `i32.const <offset>`
    so the code can use that pointer on the stack (e.g., for printing).
    """

    def __init__(self, controller):
        """
        :param controller: a WasmEmitter-like codegen context:
          - controller.current_data_offset (int)
          - controller.data_segments (list of (offset, bytes))
          - etc.
        """
        self.controller = controller

    def emit_long_array(self, node, out_lines):
        """
        Emits a 64-bit integer array to the data segments as "i64_ptr"
        and appends `i32.const <offset>` to `out_lines`.

        :param node: The AST node for ArrayLiteralExpression with:
            - "inferred_type" = "i64_ptr"
            - "elements" = list of literal or evaluated expressions
        :param out_lines: list of lines for the final WAT output
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "i64_ptr":
            raise ValueError(
                f"LongArrayLiteralEmitter: Expected 'i64_ptr', got '{inferred_type}'"
            )

        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(
            "Emitting i64_ptr array of length %d for node=%r", length, node
        )

        # 1) Build raw bytes => 4 bytes for length + 8 bytes * length
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)  # i32 array length

        # 2) For each element => evaluate + pack as 8-byte i64 (little-endian)
        for elem in elements:
            # Use your ExpressionEvaluator or other logic to get an integer
            val = ExpressionEvaluator.evaluate_expression(elem, expected_type='long')
            # Optionally range-check val in [-2**63, 2**63 - 1]
            data_bytes += struct.pack("<q", val)

        # 3) Add to data segments
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            "i64_ptr => offset=%d, size=%d bytes, elements=%d",
            offset, len(data_bytes), length
        )

        # 4) Emit 'i32.const <offset>' => pointer on the stack
        out_lines.append(f"  i32.const {offset}")
