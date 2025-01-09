# file: lmn/compiler/emitter/wasm/expressions/array_string_literal_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class StringArrayLiteralEmitter:
    """
    Emits WAT code for string array literals with proper memory layout.
    
    Responsibilities:
      - Decides whether to store the array in a static data segment (if all elements
        are simple string literals), or build the array dynamically at runtime
        (if any elements need function calls, e.g. llm("hi")).
      - Pushes the final array pointer onto the stack for further operations
        (e.g., printing).
    
    Assumptions:
      - Strings are null-terminated in memory.
      - Arrays are stored contiguously in memory starting from a base offset,
        either statically or dynamically.
      - If dynamic, you have a memory allocator function (like `call $malloc`)
        available.
    """
    
    def __init__(self, emitter):
        """
        :param emitter: Instance of WasmEmitter providing necessary utilities:
          - emitter._add_data_segment(text: str) -> int:
              Stores text in memory and returns its offset.
          - emitter.emit_expression(node, out_lines):
              Recursively emits code for expressions (e.g. FnExpression).
          - emitter.current_data_offset (int):
              Current memory offset for data segments.
          - emitter.data_segments (List):
              Append data segments as (offset, bytes).
          - emitter.request_local(name: str, wasm_type: str):
              Ensures (local $name wasm_type) is declared in the function.
        """
        self.emitter = emitter

    # -------------------------------------------------------------------------
    # Public entry point
    # -------------------------------------------------------------------------
    def emit_string_array(self, node, out_lines):
        """
        Decides whether we can do a static array or must do a dynamic approach
        (if any element is not a simple string literal). Then emits WAT code
        accordingly, leaving the final array pointer on top of the stack.
        
        :param node: AST node representing the array literal.
        :param out_lines: List to append the generated WAT code lines.
        """
        logger.debug("StringArrayLiteralEmitter: Emitting string array, node=%r", node)
        
        inferred_type = node.get("inferred_type", "")
        if inferred_type != "i32_string_array":
            logger.error(
                "StringArrayLiteralEmitter: Expected 'i32_string_array', got '%s'",
                inferred_type
            )
            raise ValueError(
                f"Unsupported inferred_type '{inferred_type}' for StringArrayLiteralEmitter."
            )

        elements = node.get("elements", [])
        if not elements:
            # No elements => just push a pointer to an empty structure
            logger.debug("StringArrayLiteralEmitter: 0 elements => _emit_empty_array()")
            self._emit_empty_array(out_lines)
        elif self._all_string_literals(elements):
            logger.debug("StringArrayLiteralEmitter: All elements are string-literals => static approach")
            self._emit_static_string_array(node, out_lines)
        else:
            logger.debug("StringArrayLiteralEmitter: Found non-literal => dynamic approach")
            self._emit_dynamic_string_array(node, out_lines)

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------
    def _all_string_literals(self, elements):
        """
        Returns True if *all* elements are LiteralExpression with literal_type
        in ("string", "i32_string"). Otherwise returns False => dynamic approach.
        """
        for elem in elements:
            if elem.get("type") != "LiteralExpression":
                return False

            # Accept both "string" & "i32_string" as "pure-literal" strings
            lit_type = elem.get("literal_type", "")
            if lit_type not in ("string", "i32_string"):
                return False
        return True

    # -------------------------------------------------------------------------
    # (1) Empty Array
    # -------------------------------------------------------------------------
    def _emit_empty_array(self, out_lines):
        logger.info("StringArrayLiteralEmitter: Emitting empty string array.")
        array_length = 0
        array_bytes = array_length.to_bytes(4, "little")  # i32 length = 0
        
        # Store the array in memory
        array_offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((array_offset, array_bytes))
        self.emitter.current_data_offset += len(array_bytes)

        logger.debug("Empty array at offset=%d, bytes=%s", array_offset, array_bytes)

        # Push array pointer
        out_lines.append(f"  i32.const {array_offset}")
        logger.debug("StringArrayLiteralEmitter: Emitted i32.const %d for empty array", array_offset)

    # -------------------------------------------------------------------------
    # (2) Static Approach (all string-literal elements)
    # -------------------------------------------------------------------------
    def _emit_static_string_array(self, node, out_lines):
        """
        Places the array in a static data segment:
          [ length (4 bytes) ][ ptr1 ][ ptr2 ]...[ ptrN ]
        """
        elements = node.get("elements", [])
        array_length = len(elements)
        logger.info("StringArrayLiteralEmitter: STATIC with %d elements", array_length)

        # 1) Gather offsets for each literal
        string_offsets = []
        for index, elem in enumerate(elements):
            string_val = elem.get("value", "")
            logger.debug("Storing string-literal '%s' @ index %d (static)", string_val, index)
            offset = self.emitter._add_data_segment(string_val)
            string_offsets.append(offset)

        # 2) Build => [length][ptr1]...[ptrN]
        length_bytes = array_length.to_bytes(4, "little")
        ptrs_bytes = b"".join(off.to_bytes(4, "little") for off in string_offsets)
        array_bytes = length_bytes + ptrs_bytes

        # 3) Store
        array_offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((array_offset, array_bytes))
        self.emitter.current_data_offset += len(array_bytes)
        logger.debug(
            "Static array => offset=%d, total_bytes=%d", array_offset, len(array_bytes)
        )

        # 4) Push pointer
        out_lines.append(f"  i32.const {array_offset}")
        logger.debug("StringArrayLiteralEmitter: Emitting i32.const %d (static pointer)", array_offset)

    # -------------------------------------------------------------------------
    # (3) Dynamic Approach
    # -------------------------------------------------------------------------
    def _emit_dynamic_string_array(self, node, out_lines):
        """
        Some elements are not "pure" (maybe a FnExpression or unknown),
        so we do:
        1) malloc(4 + 4*N)
        2) store array-length
        3) for each element => produce pointer => store in local => store at [arr + offset]
        4) push arr
        """
        elements = node.get("elements", [])
        array_length = len(elements)
        logger.info("StringArrayLiteralEmitter: DYNAMIC array => %d elements", array_length)

        # We'll declare or request local $arr : i32 for the array base,
        # and local $tmpVal : i32 for the pointer to each element.
        self.emitter.request_local("arr", "i32")
        self.emitter.request_local("tmpVal", "i32")

        # 1) total bytes: 4 for length + 4*N for pointers
        total_bytes = 4 + 4 * array_length
        logger.debug("Allocating %d bytes for dynamic array", total_bytes)
        out_lines.append(f"  i32.const {total_bytes}")
        out_lines.append("  call $malloc     ;; allocate dynamic array of that size")
        out_lines.append("  local.set $arr   ;; store base pointer in $arr")

        # 2) Store array length at [arr + 0]
        out_lines.append("  local.get $arr")
        out_lines.append("  i32.const 0")
        out_lines.append("  i32.add")
        out_lines.append(f"  i32.const {array_length}")
        out_lines.append("  i32.store")

        # 3) For each element => produce pointer => store in local $tmpVal => store at arr+offset
        for index, elem in enumerate(elements):
            pointer_offset = 4 + (index * 4)
            logger.debug("Storing element %d => arr+%d", index, pointer_offset)

            # (a) produce the pointer for the element => local.set $tmpVal
            etype = elem.get("type", "")
            lit_type = elem.get("literal_type", "")
            if etype == "LiteralExpression" and lit_type in ("string", "i32_string"):
                # string literal => store offset
                string_val = elem.get("value", "")
                offset = self.emitter._add_data_segment(string_val)
                logger.debug("Element %d => storing string offset=%d for '%s'", index, offset, string_val)
                out_lines.append(f"  i32.const {offset}")
                out_lines.append("  local.set $tmpVal")
            elif etype == "FnExpression":
                logger.debug("Element %d => FnExpression => calling self.emitter.emit_expression(...) to get pointer", index)
                self.emitter.emit_expression(elem, out_lines)  # leaves pointer on the stack
                out_lines.append("  local.set $tmpVal")
            else:
                # Fallback => store 0 pointer
                logger.warning("Element %d => unknown => i32.const 0 => local.set $tmpVal", index)
                out_lines.append("  i32.const 0")
                out_lines.append("  local.set $tmpVal")

            # (b) produce the address => arr + pointer_offset
            out_lines.append("  local.get $arr")
            out_lines.append(f"  i32.const {pointer_offset}")
            out_lines.append("  i32.add")

            # (c) push the pointer => local.get $tmpVal
            out_lines.append("  local.get $tmpVal")

            # (d) i32.store => stores that pointer
            out_lines.append("  i32.store")

        # 4) push local.get $arr => final pointer
        out_lines.append("  local.get $arr")
        logger.debug("Dynamic array => pointer on top of stack.")

