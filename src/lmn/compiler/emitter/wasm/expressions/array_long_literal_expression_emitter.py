# file: lmn/compiler/emitter/wasm/expressions/array_long_literal_expression_emitter.py

import logging
import struct

logger = logging.getLogger(__name__)

class LongArrayLiteralEmitter:
    """
    Emits WAT code for an array of 64-bit signed integers (longs) with both
    static and dynamic approaches.

    Memory layout assumptions:
      - First 4 bytes: array length (i32)
      - Then N elements, each 8 bytes of i64

    If all elements are simple 64-bit literals, do a static approach.
    Otherwise, do a dynamic approach (malloc + store).
    """

    def __init__(self, emitter):
        """
        :param emitter: A WasmEmitter-like object providing:
            - emitter._add_data_segment(text: str) -> int
            - emitter.emit_expression(node, out_lines): code to produce a value
            - emitter.current_data_offset (int)
            - emitter.data_segments (List[ (offset, bytes) ])
            - emitter.request_local(name: str, wasm_type: str)
        """
        self.emitter = emitter

    def emit_long_array(self, node, out_lines):
        """
        Main entry point. Decides static vs dynamic approach, emits WAT lines.

        The node should have:
          {
            "type": "ArrayLiteralExpression",
            "inferred_type": "i64_ptr",
            "elements": [...]
          }
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "i64_ptr":
            raise ValueError(
                f"LongArrayLiteralEmitter: Expected 'i64_ptr', got '{inferred_type}'"
            )

        elements = node.get("elements", [])
        logger.debug("LongArrayLiteralEmitter: elements=%d", len(elements))

        if not elements:
            logger.debug("No elements => _emit_empty_array()")
            self._emit_empty_array(out_lines)
        elif self._all_long_literals(elements):
            logger.debug("All elements are literal i64 => static approach")
            self._emit_static_long_array(node, out_lines)
        else:
            logger.debug("Found non-literal => dynamic approach (malloc + store i64)")
            self._emit_dynamic_long_array(node, out_lines)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _all_long_literals(self, elements):
        """
        Returns True if *all* elements are LiteralExpression with a 64-bit literal type,
        e.g. "long", "i64", or "i64_long" as needed by your DSL. Otherwise False.
        """
        for elem in elements:
            if elem.get("type") != "LiteralExpression":
                return False
            lit_type = elem.get("literal_type", "")
            # Adjust these checks if your DSL uses different literal naming
            if lit_type not in ("long", "i64_long", "i64"):
                return False
        return True

    def _emit_empty_array(self, out_lines):
        """
        Creates a 4-byte block for length=0, then pushes that pointer.
        """
        logger.info("Emitting empty long[] => 4 bytes of [0]")
        array_length = 0
        array_bytes = struct.pack("<i", array_length)  # i32 zero

        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, array_bytes))
        self.emitter.current_data_offset += len(array_bytes)

        logger.debug(
            "Empty i64-array at offset=%d, bytes=%s", offset, array_bytes.hex()
        )

        out_lines.append(f"  i32.const {offset}")
        logger.debug("Push i32.const %d for empty i64-array", offset)

    def _emit_static_long_array(self, node, out_lines):
        """
        Static approach: build [length (4 bytes)] + N*(8 bytes) in the data segment.
        """
        elements = node.get("elements", [])
        array_length = len(elements)
        logger.info("Static i64-array => %d elements", array_length)

        data_bytes = bytearray()

        # 1) array length as i32
        data_bytes += struct.pack("<i", array_length)

        # 2) each element => parse & pack as i64 little-endian
        for i, elem in enumerate(elements):
            val_str = elem.get("value", "0")
            # parse int from string, clamp or assume it's in i64 range
            val_int = int(val_str)
            val_bytes = struct.pack("<q", val_int)  # <q => little-endian 64-bit
            data_bytes += val_bytes
            logger.debug(
                "static element[%d] => %s => bytes %s",
                i, val_str, val_bytes.hex()
            )

        # 3) store in data segment
        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, data_bytes))
        self.emitter.current_data_offset += len(data_bytes)

        logger.debug(
            "Static i64-array => offset=%d, total_bytes=%d",
            offset, len(data_bytes)
        )

        # 4) push that pointer
        out_lines.append(f"  i32.const {offset}")
        logger.debug("Push i32.const %d for static i64-array", offset)

    def _emit_dynamic_long_array(self, node, out_lines):
        """
        If any element is not a pure literal => 
          1) call malloc(4 + 8*N)
          2) store length at [arr+0] (i32)
          3) for each element => produce i64 => store at [arr+4 + i*8]
          4) push arr pointer
        """
        elements = node.get("elements", [])
        array_length = len(elements)
        logger.info("Dynamic i64-array => %d elements", array_length)

        # We'll need local $arr (i32) for the pointer
        # We'll also need local $tmpVal64 (i64) to hold each element
        self.emitter.request_local("arr", "i32")
        self.emitter.request_local("tmpVal64", "i64")

        total_bytes = 4 + 8 * array_length
        logger.debug("Allocating %d bytes for dynamic i64-array", total_bytes)

        # 1) call $malloc => local.set $arr
        out_lines.append(f"  i32.const {total_bytes}")
        out_lines.append("  call $malloc")
        out_lines.append("  local.set $arr")

        # 2) store length (i32) at [arr+0]
        out_lines.append("  local.get $arr")
        out_lines.append("  i32.const 0")
        out_lines.append("  i32.add")
        out_lines.append(f"  i32.const {array_length}")
        out_lines.append("  i32.store")

        # 3) for each element => produce i64 => store in local => i64.store
        for i, elem in enumerate(elements):
            elem_offset = 4 + i * 8
            logger.debug("Element[%d] => arr+%d", i, elem_offset)

            etype = elem.get("type", "")
            lit_type = elem.get("literal_type", "")
            if etype == "LiteralExpression" and lit_type in ("long", "i64_long", "i64"):
                # simple literal => parse
                val_str = elem.get("value", "0")
                val_int = int(val_str)  # assume in 64-bit range
                logger.debug(
                    "Element[%d] => literal i64=%d => local.set $tmpVal64", i, val_int
                )
                out_lines.append(f"  i64.const {val_int}")
                out_lines.append("  local.set $tmpVal64")
            elif etype == "FnExpression":
                logger.debug(
                    "Element[%d] => FnExpression => emit code to produce i64 => local.set $tmpVal64", i
                )
                # your emitter should push i64 on the stack
                self.emitter.emit_expression(elem, out_lines)
                out_lines.append("  local.set $tmpVal64")
            else:
                logger.warning("Element[%d] => unknown => fallback i64.const 0 => local.set $tmpVal64", i)
                out_lines.append("  i64.const 0")
                out_lines.append("  local.set $tmpVal64")

            # store that i64 at [arr + elem_offset]
            out_lines.append("  local.get $arr")
            out_lines.append(f"  i32.const {elem_offset}")
            out_lines.append("  i32.add")
            out_lines.append("  local.get $tmpVal64")
            out_lines.append("  i64.store")

        # 4) final => local.get $arr => pointer on stack
        out_lines.append("  local.get $arr")
        logger.debug("Dynamic i64-array => pointer on stack.")
