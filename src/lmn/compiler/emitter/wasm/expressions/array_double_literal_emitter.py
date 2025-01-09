# file: lmn/compiler/emitter/wasm/expressions/array_double_literal_expression_emitter.py

import struct
import logging

logger = logging.getLogger(__name__)

class DoubleArrayLiteralEmitter:
    """
    Emits WAT code for a double[] (64-bit float) array, allowing both
    static and dynamic approaches.

    Memory layout:
      - 4 bytes for the array length (i32)
      - then N elements, each 8 bytes as a little-endian f64

    If all elements are simple float64 literals, we embed them statically.
    Otherwise, we call malloc(...) and store each element at runtime.
    """

    def __init__(self, emitter):
        """
        :param emitter: a WasmEmitter-like object that provides:
          - emitter._add_data_segment(text: str) -> int
          - emitter.emit_expression(node, out_lines): code that yields f64 on stack
          - emitter.current_data_offset (int)
          - emitter.data_segments (List of (offset, bytes))
          - emitter.request_local(name: str, wasm_type: str)
        """
        self.emitter = emitter

    def emit_double_array(self, node, out_lines):
        """
        Main entry point. Decides static vs. dynamic approach, then emits
        instructions that leave the array pointer (i32) on the stack.

        The AST node looks like:
          {
            "type": "ArrayLiteralExpression",
            "inferred_type": "f64_ptr",
            "elements": [...]
          }
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "f64_ptr":
            raise ValueError(
                f"DoubleArrayLiteralEmitter: expected 'f64_ptr', got '{inferred_type}'"
            )

        elements = node.get("elements", [])
        logger.debug("DoubleArrayLiteralEmitter: %d elements", len(elements))

        if not elements:
            logger.debug("No elements => _emit_empty_array()")
            self._emit_empty_array(out_lines)
        elif self._all_double_literals(elements):
            logger.debug("All elements are double-literals => static approach")
            self._emit_static_double_array(node, out_lines)
        else:
            logger.debug("At least one element is not a pure literal => dynamic approach")
            self._emit_dynamic_double_array(node, out_lines)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _all_double_literals(self, elements):
        """
        Returns True if every element is a LiteralExpression with literal_type
        in ("double", "f64"). Otherwise False => dynamic approach.
        """
        for elem in elements:
            if elem.get("type") != "LiteralExpression":
                return False
            lit_type = elem.get("literal_type", "")
            if lit_type not in ("double", "f64"):
                return False
        return True

    # -------------------------------------------------------------------------
    # (1) Empty Array
    # -------------------------------------------------------------------------
    def _emit_empty_array(self, out_lines):
        """
        Minimal data segment: 4 bytes => length=0. Push pointer.
        """
        logger.info("Emitting empty f64[] => 4 bytes (length=0)")
        data_bytes = struct.pack("<i", 0)  # i32=0 => length

        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, data_bytes))
        self.emitter.current_data_offset += len(data_bytes)

        logger.debug(
            "Empty double-array => offset=%d, bytes=%s",
            offset, data_bytes.hex()
        )
        out_lines.append(f"  i32.const {offset}")
        logger.debug("Push i32.const %d for empty double-array", offset)

    # -------------------------------------------------------------------------
    # (2) Static Approach
    # -------------------------------------------------------------------------
    def _emit_static_double_array(self, node, out_lines):
        """
        Encodes [length (i32)] + N*(8 bytes of f64) in a static data segment,
        then emits i32.const offset => pointer.
        """
        elements = node.get("elements", [])
        length = len(elements)
        logger.info("Static f64 array => %d elements", length)

        data_bytes = bytearray()
        # 1) array length
        data_bytes += struct.pack("<i", length)

        # 2) each element => 8 bytes
        for i, elem in enumerate(elements):
            # parse from string => float => pack as double
            val_str = str(elem.get("value", "0"))
            try:
                val_d = float(val_str)
            except ValueError:
                logger.warning(
                    "Element[%d]='%s' not parseable as double => default=0.0", i, val_str
                )
                val_d = 0.0

            packed = struct.pack("<d", val_d)
            data_bytes += packed
            logger.debug(
                "static element[%d] => %s => bytes %s",
                i, val_d, packed.hex()
            )

        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, data_bytes))
        self.emitter.current_data_offset += len(data_bytes)

        logger.debug(
            "Static f64-array => offset=%d, total_bytes=%d",
            offset, len(data_bytes)
        )
        out_lines.append(f"  i32.const {offset}")
        logger.debug("Push i32.const %d for static f64-array", offset)

    # -------------------------------------------------------------------------
    # (3) Dynamic Approach
    # -------------------------------------------------------------------------
    def _emit_dynamic_double_array(self, node, out_lines):
        """
        1) malloc(4 + 8*N)
        2) store array length
        3) for each element => produce f64 => store at arr+4 + 8*i
        4) push arr
        """
        elements = node.get("elements", [])
        length = len(elements)
        logger.info("Dynamic f64-array => %d elements", length)

        # We'll declare local $arr : i32, local $tmpValF64 : f64
        self.emitter.request_local("arr", "i32")
        self.emitter.request_local("tmpValF64", "f64")

        total_bytes = 4 + 8 * length
        logger.debug("Allocating %d bytes for dynamic f64-array", total_bytes)

        # 1) call malloc => local.set $arr
        out_lines.append(f"  i32.const {total_bytes}")
        out_lines.append("  call $malloc")
        out_lines.append("  local.set $arr")

        # 2) store length at [arr + 0]
        out_lines.append("  local.get $arr")
        out_lines.append("  i32.const 0")
        out_lines.append("  i32.add")
        out_lines.append(f"  i32.const {length}")
        out_lines.append("  i32.store")

        # 3) each element => produce f64 => local.set $tmpValF64 => store
        for i, elem in enumerate(elements):
            elem_offset = 4 + i * 8
            logger.debug("Element[%d] => arr+%d", i, elem_offset)

            etype = elem.get("type", "")
            lit_type = elem.get("literal_type", "")

            if etype == "LiteralExpression" and lit_type in ("double", "f64"):
                val_str = str(elem.get("value", "0.0"))
                try:
                    val_d = float(val_str)
                except ValueError:
                    logger.warning(
                        "Element[%d] => '%s' invalid => default 0.0",
                        i, val_str
                    )
                    val_d = 0.0
                logger.debug(
                    "Element[%d] => literal f64=%.4f => local.set $tmpValF64",
                    i, val_d
                )
                out_lines.append(f"  f64.const {val_d}")
                out_lines.append("  local.set $tmpValF64")

            elif etype == "FnExpression":
                logger.debug(
                    "Element[%d] => FnExpression => calling emitter.emit_expression(...) => local.set $tmpValF64",
                    i
                )
                self.emitter.emit_expression(elem, out_lines)  # top of stack => f64
                out_lines.append("  local.set $tmpValF64")

            else:
                logger.warning(
                    "Element[%d] => unknown => f64.const 0 => local.set $tmpValF64",
                    i
                )
                out_lines.append("  f64.const 0")
                out_lines.append("  local.set $tmpValF64")

            # store at [arr + elem_offset]
            out_lines.append("  local.get $arr")
            out_lines.append(f"  i32.const {elem_offset}")
            out_lines.append("  i32.add")

            out_lines.append("  local.get $tmpValF64")
            # In WebAssembly, we do: `f64.store` => 8 bytes
            out_lines.append("  f64.store")

        # 4) final => local.get $arr => pointer
        out_lines.append("  local.get $arr")
        logger.debug("Dynamic f64-array => pointer on stack.")
