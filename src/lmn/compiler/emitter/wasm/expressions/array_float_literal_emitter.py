# file: lmn/compiler/emitter/wasm/expressions/array_float_literal_expression_emitter.py

import struct
import logging

logger = logging.getLogger(__name__)

class FloatArrayLiteralEmitter:
    """
    Emits WAT code for a float[] (32-bit float) array with both
    static and dynamic approaches.

    Memory layout:
      - 4 bytes for array length (i32)
      - then N elements, each 4 bytes in little-endian f32

    If all elements are simple float literals, do a static approach.
    Otherwise, do a dynamic approach (malloc + store).
    """

    def __init__(self, emitter):
        """
        :param emitter: A WasmEmitter-like object providing:
            - emitter._add_data_segment(text: str) -> int
            - emitter.emit_expression(node, out_lines): code that leaves a float on stack
            - emitter.current_data_offset (int)
            - emitter.data_segments (List[(offset, bytes)])
            - emitter.request_local(name: str, wasm_type: str)
        """
        self.emitter = emitter

    def emit_float_array(self, node, out_lines):
        """
        Main entry point. Chooses static vs. dynamic array approach.

        The AST node should look like:
          {
            "type": "ArrayLiteralExpression",
            "inferred_type": "f32_ptr",
            "elements": [...]
          }
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "f32_ptr":
            raise ValueError(
                f"FloatArrayLiteralEmitter: expected 'f32_ptr', got '{inferred_type}'"
            )

        elements = node.get("elements", [])
        logger.debug("FloatArrayLiteralEmitter: %d elements", len(elements))

        if not elements:
            logger.debug("No elements => _emit_empty_array()")
            self._emit_empty_array(out_lines)
        elif self._all_float_literals(elements):
            logger.debug("All elements are float literals => static approach")
            self._emit_static_float_array(node, out_lines)
        else:
            logger.debug("Some element not a literal => dynamic approach (malloc + f32.store)")
            self._emit_dynamic_float_array(node, out_lines)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _all_float_literals(self, elements):
        """
        Returns True if *all* elements are LiteralExpression with literal_type
        in ("float", "f32"). Otherwise returns False => dynamic approach.
        """
        for elem in elements:
            if elem.get("type") != "LiteralExpression":
                return False
            lit_type = elem.get("literal_type", "")
            if lit_type not in ("float", "f32"):
                return False
        return True

    # -------------------------------------------------------------------------
    # (1) Empty Array
    # -------------------------------------------------------------------------
    def _emit_empty_array(self, out_lines):
        """
        Creates a 4-byte block for length=0, then pushes that pointer.
        """
        logger.info("Emitting empty float[] => just 4 bytes of i32=0 length")
        array_length = 0
        data_bytes = struct.pack("<i", array_length)  # i32 zero

        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, data_bytes))
        self.emitter.current_data_offset += len(data_bytes)

        logger.debug("Empty f32-array => offset=%d, bytes=%s", offset, data_bytes.hex())

        out_lines.append(f"  i32.const {offset}")
        logger.debug("Push i32.const %d for empty f32-array", offset)

    # -------------------------------------------------------------------------
    # (2) Static Approach
    # -------------------------------------------------------------------------
    def _emit_static_float_array(self, node, out_lines):
        """
        Encodes [length (4 bytes)] + N*(4 bytes of f32) in data segment.
        Then i32.const offset => pointer.
        """
        elements = node.get("elements", [])
        length = len(elements)
        logger.info("Static f32-array => %d elements", length)

        data_bytes = bytearray()
        # 1) array length
        data_bytes += struct.pack("<i", length)

        # 2) each float => 4 bytes
        for i, elem in enumerate(elements):
            val_str = str(elem.get("value", "0"))
            # parse as float
            try:
                val_f = float(val_str)
            except ValueError:
                logger.warning("Element[%d] = '%s' not parseable as float => default 0.0", i, val_str)
                val_f = 0.0

            packed = struct.pack("<f", val_f)
            data_bytes += packed
            logger.debug("static element[%d] => %s => bytes %s", i, val_f, packed.hex())

        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, data_bytes))
        self.emitter.current_data_offset += len(data_bytes)

        logger.debug("Static f32-array => offset=%d, total_bytes=%d", offset, len(data_bytes))

        out_lines.append(f"  i32.const {offset}")
        logger.debug("Push i32.const %d for static f32-array", offset)

    # -------------------------------------------------------------------------
    # (3) Dynamic Approach
    # -------------------------------------------------------------------------
    def _emit_dynamic_float_array(self, node, out_lines):
        """
        - malloc(4 + 4*N)
        - store array length
        - for each element => produce float => store at arr+4 + i*4
        - push arr
        """
        elements = node.get("elements", [])
        length = len(elements)
        logger.info("Dynamic f32-array => %d elements", length)

        # we'll use local $arr : i32, local $tmpVal : f32
        self.emitter.request_local("arr", "i32")
        self.emitter.request_local("tmpValF32", "f32")

        total_bytes = 4 + 4 * length
        logger.debug("Allocating %d bytes for dynamic f32-array", total_bytes)

        # 1) call malloc => local.set $arr
        out_lines.append(f"  i32.const {total_bytes}")
        out_lines.append("  call $malloc")
        out_lines.append("  local.set $arr")

        # 2) store length at [arr+0]
        out_lines.append("  local.get $arr")
        out_lines.append("  i32.const 0")
        out_lines.append("  i32.add")
        out_lines.append(f"  i32.const {length}")
        out_lines.append("  i32.store")

        # 3) each element => produce float => store in local => f32.store
        for i, elem in enumerate(elements):
            elem_offset = 4 + i * 4
            logger.debug("Element[%d] => arr+%d", i, elem_offset)

            etype = elem.get("type", "")
            lit_type = elem.get("literal_type", "")

            if etype == "LiteralExpression" and lit_type in ("float", "f32"):
                val_str = str(elem.get("value", "0"))
                try:
                    val_f = float(val_str)
                except ValueError:
                    logger.warning("Element[%d] => '%s' invalid => 0.0", i, val_str)
                    val_f = 0.0
                logger.debug("Element[%d] => literal f32=%.3f => local.set $tmpValF32", i, val_f)
                out_lines.append(f"  f32.const {val_f}")
                out_lines.append("  local.set $tmpValF32")
            elif etype == "FnExpression":
                logger.debug("Element[%d] => FnExpression => emit code => local.set $tmpValF32", i)
                self.emitter.emit_expression(elem, out_lines)  # stack has f32
                out_lines.append("  local.set $tmpValF32")
            else:
                logger.warning("Element[%d] => unknown => f32.const 0 => local.set $tmpValF32", i)
                out_lines.append("  f32.const 0")
                out_lines.append("  local.set $tmpValF32")

            # store at [arr + elem_offset]
            out_lines.append("  local.get $arr")
            out_lines.append(f"  i32.const {elem_offset}")
            out_lines.append("  i32.add")
            out_lines.append("  local.get $tmpValF32")
            out_lines.append("  f32.store")

        # 4) final => local.get $arr => pointer
        out_lines.append("  local.get $arr")
        logger.debug("Dynamic f32-array => pointer on stack.")
