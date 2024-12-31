# file: lmn/compiler/emitter/wasm/expressions/array_int_literal_expression_emitter.py
import struct
import logging

logger = logging.getLogger(__name__)

class IntArrayLiteralEmitter:
    """
    Builds a memory block for 'int[]' arrays in WebAssembly:
      - 4 bytes for array length (i32),
      - Followed by 'length' elements, each 4 bytes (i32 in little-endian).

    That block is placed in a data segment, and we emit 'i32.const <offset>'
    so the Wasm code can push that pointer on the stack.
    
    Example usage:
      node = {
        "type": "ArrayLiteralExpression",
        "inferred_type": "int[]",
        "elements": [
          {"type": "LiteralExpression", "value": 10},
          {"type": "LiteralExpression", "value": 20},
        ]
      }
    """

    def __init__(self, controller):
        """
        :param controller: typically your WasmEmitter or a similar codegen
                           context that provides:
         - controller.current_data_offset (int) => next free memory offset
         - controller.data_segments (list of (offset, bytes)) => data segments
         - controller.emit_expression(expr, out_lines) => if you need nested calls
        """
        self.controller = controller

    def emit_int_array(self, node, out_lines):
        """
        node sample:
        {
          "type": "ArrayLiteralExpression",
          "inferred_type": "int[]",
          "elements": [
            {"type": "LiteralExpression", "value": 1, ...},
            {"type": "LiteralExpression", "value": 2, ...}
          ]
        }

        We'll construct a bytearray like:
          [ length:i32, elem0:i32, elem1:i32, ... ]

        Then store it in a data segment at an available offset, update
        'controller.current_data_offset', and finally emit 'i32.const <offset>'
        so the code sees that pointer on the stack.
        """
        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(f"Emitting int[] of length {length} for node={node}")

        # 1) Build raw bytes (little-endian) => 4 bytes for length, then each i32 element
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)  # array length as i32

        # 2) Process each element as 32-bit int
        for elem in elements:
            val = elem.get("value", 0)

            # (A) Ensure it's actually an integer
            if not isinstance(val, int):
                logger.warning(f"Non-integer value {val} in int[]; defaulting to 0.")
                val = 0

            # (B) Optional: check 32-bit range
            # if val < -2**31 or val > 2**31 - 1:
            #     logger.warning(f"Value {val} out of 32-bit int range; clamping or defaulting.")
            #     val = 0

            data_bytes += struct.pack("<i", val)

        # 3) Allocate a segment offset
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            f"int[] memory block => offset={offset}, size={len(data_bytes)} bytes, elements={length}"
        )

        # 4) Emit instructions => 'i32.const offset'
        #    This places the pointer on the stack for the caller to store/use
        out_lines.append(f"  i32.const {offset}")
