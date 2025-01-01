import struct
import logging
from .expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)

class IntArrayLiteralEmitter:
    """
    Builds a memory block for arrays of 32-bit integers in WebAssembly.
    We assume the lowered type is "i32_ptr" for an array of i32.

    Memory layout:
      [ length (4 bytes) ][ value1 (4 bytes) ][ value2 (4 bytes) ] ...
    """

    def __init__(self, controller):
        """
        :param controller: Your WasmEmitter or codegen context, providing:
          - controller.current_data_offset (int)
          - controller.data_segments (list of (offset, bytes))
          - etc.
        """
        self.controller = controller

    def emit_int_array(self, node, out_lines):
        """
        Emits an i32_ptr array with detailed logging of memory layout.
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "i32_ptr":
            raise ValueError(f"IntArrayLiteralEmitter: Expected 'i32_ptr', got '{inferred_type}'")

        elements = node.get("elements", [])
        length = len(elements)
        logger.debug(f"Starting int array emission: length={length}, node={node}")

        # 1) Evaluate each element as i32
        values = []
        for i, elem in enumerate(elements):
            try:
                # Evaluate as 32-bit integer
                val = ExpressionEvaluator.evaluate_expression(elem, expected_type='int')
                val = ExpressionEvaluator.clamp_value(val, 'int')  # ensure i32 range
                values.append(val)
                logger.debug(f"Element[{i}] evaluated to {val}")
            except Exception as e:
                logger.error(f"Failed to evaluate element {i}: {e}")
                values.append(0)

        # 2) Construct the memory bytes
        data_bytes = bytearray()

        # First 4 bytes => array length (i32)
        data_bytes += struct.pack("<i", length)
        logger.debug(f"Length bytes: {data_bytes.hex()}")

        # Next => each element as i32
        for i, val in enumerate(values):
            val_bytes = struct.pack("<i", val)
            data_bytes += val_bytes
            logger.debug(f"Value[{i}]={val} bytes: {val_bytes.hex()}")

        # 3) Store in memory
        offset = self.controller.current_data_offset
        self.controller.data_segments.append((offset, data_bytes))
        logger.debug(
            "Array stored at offset=%d, total_size=%d", 
            offset, len(data_bytes)
        )

        # Update offset for future allocations
        self.controller.current_data_offset += len(data_bytes)
        logger.debug(f"New current_data_offset={self.controller.current_data_offset}")

        # 4) Push array pointer onto stack
        out_lines.append(f"  i32.const {offset}")
        logger.debug(f"Emitted i32.const {offset}")

        return offset  # For debugging/tracking
