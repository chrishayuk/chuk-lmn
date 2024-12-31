# file: lmn/compiler/emitter/wasm/expressions/array_long_literal_expression_emitter.py

import struct
import logging

logger = logging.getLogger(__name__)

class LongArrayLiteralEmitter:
    """
    Emits a Wasm-friendly memory block for `long[]` arrays (64-bit signed integers).
    The layout is:
      - 4 bytes for the array length (i32)
      - 'length' elements, each 8 bytes (i64, little-endian)

    This emitter then places the data block into a data segment of your Wasm module
    and emits 'i32.const <offset>' so the code can push that pointer on the stack.

    Usage example:
      node = {
        "type": "ArrayLiteralExpression",
        "inferred_type": "long[]",  # or 'i64_ptr' after lowering
        "elements": [
          { "type": "LiteralExpression", "value": 10000000000, ... },
          { "type": "LiteralExpression", "value": -1234567890123456789, ... },
          ...
        ]
      }
    """

    def __init__(self, controller):
        """
        :param controller: typically your main WasmEmitter or codegen context,
                           which provides:
         - controller.current_data_offset: int => next free memory offset
         - controller.data_segments: list of (offset, bytes)
         - controller.emit_expression(expr, out_lines) if you want nested calls
        """
        self.controller = controller

    def emit_long_array(self, node, out_lines):
        """
        node structure example:
        {
          "type": "ArrayLiteralExpression",
          "inferred_type": "long[]",
          "elements": [
            { "type": "LiteralExpression", "value": 100000, ... },
            { "type": "LiteralExpression", "value": -9999999, ... },
            ...
          ]
        }

        We'll build bytes in the layout:
          <length : i32>  <elem0 : i64> <elem1 : i64> ...
        Then store them in a data segment at some offset.
        We'll emit `i32.const <offset>` to place that pointer on the stack.
        """
        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(f"Emitting long[] of length {length} for node={node}")

        # 1) Build raw bytes => first 4 bytes for 'length'
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)  # i32: number of elements

        # 2) For each element => 8 bytes as i64 in little-endian
        for elem in elements:
            val = elem.get("value", 0)
            
            # Check the Python value is actually int, fallback if not
            if not isinstance(val, int):
                logger.warning(f"Non-integer value {val} in long[]; defaulting to 0.")
                val = 0

            # Optional: Range check for 64-bit signed integers (if desired)
            #   if val < -2**63 or val > 2**63 - 1:
            #       logger.warning(f"Value {val} out of 64-bit range, clamping or defaulting.")
            #       val = 0

            # Pack as 8-byte little-endian integer
            data_bytes += struct.pack("<q", val)

        # 3) Determine offset in memory; append to data_segments
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            f"long[] memory block => offset={offset}, size={len(data_bytes)} bytes, elements={length}"
        )

        # 4) Emit instructions => push the pointer (offset) on the stack
        out_lines.append(f"  i32.const {offset}")
