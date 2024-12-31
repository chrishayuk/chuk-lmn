# file: lmn/compiler/emitter/wasm/expressions/array_float_literal_expression_emitter.py

import struct
import logging

logger = logging.getLogger(__name__)

class FloatArrayLiteralEmitter:
    """
    Builds a memory block for `float[]` arrays (32-bit floats).
    Layout in memory:
      - 4 bytes for array length (i32)
      - 'length' elements, each 4 bytes (f32, little-endian)

    We place this block in the data segment, returning an i32 pointer.
    """

    def __init__(self, controller):
        """
        :param controller: typically your WasmEmitter or codegen context, providing:
         - controller.current_data_offset: next free memory offset (int)
         - controller.data_segments: list of (offset, bytes)
         - controller.emit_expression(expr, out_lines) for nested calls if needed
        """
        self.controller = controller

    def emit_float_array(self, node, out_lines):
        """
        Example node:
        {
          "type": "ArrayLiteralExpression",
          "inferred_type": "float[]",
          "elements": [
            { "type": "LiteralExpression", "value": 1.0, ... },
            { "type": "LiteralExpression", "value": 2.5, ... },
            ...
          ]
        }

        We'll build bytes in the layout:
            <length : i32> <elem0 : f32> <elem1 : f32> ...
        Then store them in a data segment. We'll emit `i32.const <offset>` 
        so the pointer is pushed onto the stack.
        """
        elements = node.get("elements", [])
        length = len(elements)

        logger.debug(f"Emitting float[] of length {length} for node={node}")

        # 1) Build raw bytes: first 4 bytes => length (i32)
        data_bytes = bytearray()
        data_bytes += struct.pack("<i", length)

        # 2) Each element => 4 bytes (f32) in little-endian
        for elem in elements:
            val = elem.get("value", 0.0)
            # If not numeric, fallback to 0.0
            if not isinstance(val, (int, float)):
                logger.warning(f"Non-float value {val} in float[]; defaulting to 0.0")
                val = 0.0

            # Convert to float in case it was an int
            val = float(val)

            # Pack as 32-bit float
            data_bytes += struct.pack("<f", val)

        # 3) Add to data segment => get an offset
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        self.controller.current_data_offset += len(data_bytes)

        logger.debug(
            f"float[] memory block => offset={offset}, size={len(data_bytes)} bytes, elements={length}"
        )

        # 4) Emit instructions => push that offset as i32
        out_lines.append(f"  i32.const {offset}")
