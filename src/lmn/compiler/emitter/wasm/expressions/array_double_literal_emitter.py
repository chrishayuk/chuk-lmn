# file: lmn/compiler/emitter/wasm/expressions/array_double_literal_expression_emitter.py

import struct
import logging

logger = logging.getLogger(__name__)

class DoubleArrayLiteralEmitter:
    """
    Builds a memory block for `double[]` arrays (64-bit floats).
    Layout in memory:
      - 4 bytes for array length (i32)
      - 'length' elements, each 8 bytes (f64, little-endian)

    We place this block in a data segment, returning an i32 pointer.
    """

    def __init__(self, controller):
        """
        :param controller: your WasmEmitter or codegen context, providing:
         - controller.current_data_offset: next free memory offset (int)
         - controller.data_segments: list of (offset, bytes)
         - controller.emit_expression(expr, out_lines) if needed
        """
        self.controller = controller

    def emit_double_array(self, node, out_lines):
        """
        Example node:
        {
          "type": "ArrayLiteralExpression",
          "inferred_type": "double[]",
          "elements": [
            { "type": "LiteralExpression", "value": 1.0, ... },
            { "type": "LiteralExpression", "value": 2.5, ... },
            ...
          ]
        }

        We'll build bytes in the layout:
            <length : i32> <elem0 : f64> <elem1 : f64> ...
        Then store them in a data segment. We'll emit `i32.const <offset>`
        so the pointer is on the stack.
        """
        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(f"Emitting double[] of length {length} for node={node}")

        # 1) 4 bytes => length (i32)
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)

        # 2) Each element => 8 bytes (f64) in little-endian
        for elem in elements:
            val = elem.get("value", 0.0)
            # If not numeric, fallback to 0.0
            if not isinstance(val, (int, float)):
                logger.warning(f"Non-numeric value {val} in double[]; defaulting to 0.0")
                val = 0.0

            val = float(val)  # ensure we have a float type
            data_bytes += struct.pack("<d", val)

        # 3) Insert into data segments => get offset
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            f"double[] memory block => offset={offset}, size={len(data_bytes)} bytes, elements={length}"
        )

        # 4) Emit instructions => push offset
        out_lines.append(f"  i32.const {offset}")
