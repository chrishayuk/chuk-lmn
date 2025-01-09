# file: lmn/compiler/emitter/wasm/expressions/array_int_literal_expression_emitter.py

import logging
import struct

logger = logging.getLogger(__name__)

class IntArrayLiteralEmitter:
    """
    Emits WAT code for int array literals (32-bit integers) with both static and dynamic approaches.
    
    - Static if all elements are pure integer literals.
    - Dynamic if any element requires a function call or other runtime logic (like a FnExpression).
    """

    def __init__(self, emitter):
        """
        :param emitter: Instance of WasmEmitter (or similar) providing:
            - emitter._add_data_segment(text: str) -> int
            - emitter.emit_expression(node, out_lines)
            - emitter.current_data_offset (int)
            - emitter.data_segments (List)
            - emitter.request_local(name: str, wasm_type: str)
        """
        self.emitter = emitter

    def emit_int_array(self, node, out_lines):
        """
        Main entry point: decides static vs. dynamic approach, then emits the WAT code
        that leaves the final array pointer on top of the stack.
        """
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "i32_ptr":
            raise ValueError(f"IntArrayLiteralEmitter: Expected 'i32_ptr', got '{inferred_type}'")

        elements = node.get("elements", [])
        logger.debug("Emitting int array with %d elements", len(elements))

        if not elements:
            # An empty array => just push a pointer to a 0-length block
            logger.debug("No elements => emit_empty_array()")
            self._emit_empty_array(out_lines)
        elif self._all_int_literals(elements):
            logger.debug("All elements are int-literals => static approach")
            self._emit_static_int_array(node, out_lines)
        else:
            logger.debug("Found non-literal => dynamic approach (malloc + store)")
            self._emit_dynamic_int_array(node, out_lines)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _all_int_literals(self, elements):
        """
        Returns True if *all* elements are integer literal expressions 
        that can be resolved statically. Otherwise, dynamic approach.
        """
        for elem in elements:
            if elem.get("type") != "LiteralExpression":
                return False
            lit_type = elem.get("literal_type", "")
            # In many DSLs, you'd see 'int', 'i32', 'i32_int', etc.
            # Adjust as needed for your DSL’s naming.
            if lit_type not in ("int", "i32_int", "i32"):
                return False
        return True

    def _emit_empty_array(self, out_lines):
        """
        Creates a 4-byte block [length=0].
        """
        logger.info("Emitting empty int array => [0 length]")
        array_length = 0
        array_bytes = struct.pack("<i", array_length)

        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, array_bytes))
        self.emitter.current_data_offset += len(array_bytes)

        logger.debug("Empty int-array at offset=%d, bytes=%s", offset, array_bytes.hex())

        # Push array pointer
        out_lines.append(f"  i32.const {offset}")
        logger.debug("Pushed offset %d for empty int array", offset)

    def _emit_static_int_array(self, node, out_lines):
        """
        If all elements are integer literals, we can store them directly in the data segment:
          [ length (4 bytes) ][ val1 (4 bytes) ][ val2 (4 bytes) ] ...
        """
        elements = node.get("elements", [])
        array_length = len(elements)
        logger.info("Static int-array with %d elements", array_length)

        data_bytes = bytearray()

        # 1) length
        data_bytes += struct.pack("<i", array_length)

        # 2) each element as i32
        for i, elem in enumerate(elements):
            # Because it's static, the DSL said it's a literal => get value
            val_str = elem.get("value", "0")
            val_int = int(val_str)  # or parse if needed
            val_bytes = struct.pack("<i", val_int)
            data_bytes += val_bytes
            logger.debug("Static element[%d] = %s => bytes %s", i, val_str, val_bytes.hex())

        # 3) store in data segment
        offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((offset, data_bytes))
        self.emitter.current_data_offset += len(data_bytes)

        logger.debug(
            "Static int-array => offset=%d, total_bytes=%d", 
            offset, len(data_bytes)
        )

        # 4) push the pointer
        out_lines.append(f"  i32.const {offset}")
        logger.debug("Pushed i32.const %d for static int-array", offset)

    def _emit_dynamic_int_array(self, node, out_lines):
        """
        If any element is not a pure literal, we do:
          1) i32.const (4 + 4*N) => call $malloc => local.set $arr
          2) store length at [arr+0]
          3) for each element => evaluate => store in local => store at [arr + 4 + i*4]
          4) final => local.get $arr => push
        """
        elements = node.get("elements", [])
        array_length = len(elements)
        logger.info("Dynamic int-array => %d elements", array_length)

        # Request local variables
        self.emitter.request_local("arr", "i32")
        self.emitter.request_local("tmpVal", "i32")

        total_bytes = 4 + 4 * array_length
        logger.debug("Allocating %d bytes for dynamic int-array", total_bytes)

        # 1) call $malloc
        out_lines.append(f"  i32.const {total_bytes}")
        out_lines.append("  call $malloc")
        out_lines.append("  local.set $arr")

        # 2) store array_length at [arr + 0]
        out_lines.append("  local.get $arr")
        out_lines.append("  i32.const 0")
        out_lines.append("  i32.add")
        out_lines.append(f"  i32.const {array_length}")
        out_lines.append("  i32.store")

        # 3) for each element => produce int => store to [arr + 4 + i*4]
        for i, elem in enumerate(elements):
            offset = 4 + i * 4
            logger.debug("Storing element[%d] => arr+%d", i, offset)

            etype = elem.get("type", "")
            lit_type = elem.get("literal_type", "")
            if etype == "LiteralExpression" and lit_type in ("int", "i32_int", "i32"):
                # statically known int => parse => push => local.set $tmpVal
                val_str = elem.get("value", "0")
                val_int = int(val_str)
                logger.debug("Element[%d] => literal int=%d", i, val_int)
                out_lines.append(f"  i32.const {val_int}")
                out_lines.append("  local.set $tmpVal")
            elif etype == "FnExpression":
                # like with strings, we do expression => local.set $tmpVal
                logger.debug("Element[%d] => FnExpression => emit code to produce i32", i)
                self.emitter.emit_expression(elem, out_lines)
                out_lines.append("  local.set $tmpVal")
            else:
                # fallback => store 0
                logger.warning("Element[%d] => unknown => fallback i32.const 0 => local.set $tmpVal", i)
                out_lines.append("  i32.const 0")
                out_lines.append("  local.set $tmpVal")

            # store at arr+offset
            out_lines.append("  local.get $arr")
            out_lines.append(f"  i32.const {offset}")
            out_lines.append("  i32.add  ;; address for element")
            out_lines.append("  local.get $tmpVal")
            out_lines.append("  i32.store")

        # 4) push local.get $arr => final pointer
        out_lines.append("  local.get $arr")
        logger.debug("Dynamic int-array => pointer on top of stack.")
