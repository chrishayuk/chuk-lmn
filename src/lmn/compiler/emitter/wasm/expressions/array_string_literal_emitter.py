# file: lmn/compiler/emitter/wasm/expressions/array_string_literal_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class StringArrayLiteralEmitter:
    """
    Emits WAT code for string array literals with proper memory layout.
    
    Responsibilities:
      - Stores each string in a separate data segment and records their memory offsets.
      - Constructs an array structure in memory containing the length and pointers to these strings.
      - Pushes the array pointer onto the stack for further operations (e.g., printing).
    
    Assumptions:
      - Strings are null-terminated in memory.
      - Arrays are stored contiguously in memory starting from a base offset.
    """
    
    def __init__(self, emitter):
        """
        Initializes the StringArrayLiteralEmitter.
        
        :param emitter: Instance of WasmEmitter providing necessary utilities:
            - emitter._add_data_segment(text: str) -> int: Stores text in memory and returns its offset.
            - emitter.current_data_offset: Current memory offset for data segments.
            - emitter.data_segments: List to append data segments as (offset, bytes).
        """
        self.emitter = emitter
    
    def emit_string_array(self, node, out_lines):
        """
        Emits WAT code for a string array literal.
        
        :param node: AST node representing the array literal.
        :param out_lines: List to append the generated WAT code lines.
        """
        logger.debug("StringArrayLiteralEmitter: Emitting string array, node=%r", node)
        
        elements = node.get("elements", [])
        inferred_type = node.get("inferred_type", "")
        
        # Validate inferred type
        if inferred_type != "i32_string_array":
            logger.error(
                "StringArrayLiteralEmitter: Expected inferred_type 'i32_string_array', got '%s'",
                inferred_type
            )
            raise ValueError(
                f"Unsupported inferred_type '{inferred_type}' for StringArrayLiteralEmitter."
            )
        
        # Handle empty arrays
        if not elements:
            logger.info("StringArrayLiteralEmitter: Empty string array detected.")
            array_length = 0
            array_bytes = array_length.to_bytes(4, byteorder='little')  # i32 length = 0
            
            # Store the array in memory
            array_offset = self.emitter.current_data_offset
            self.emitter.data_segments.append((array_offset, array_bytes))
            self.emitter.current_data_offset += len(array_bytes)
            logger.debug(
                "StringArrayLiteralEmitter: Stored empty array at memory offset %d with bytes %s",
                array_offset, array_bytes
            )
            
            # Push array pointer onto stack
            out_lines.append(f"  i32.const {array_offset}")
            logger.debug(
                "StringArrayLiteralEmitter: Emitted 'i32.const %d' for empty array", 
                array_offset
            )
            return
        
        string_offsets = []
        array_length = len(elements)
        
        logger.debug("StringArrayLiteralEmitter: Array length = %d", array_length)
        
        # Iterate over each element to store strings and collect their offsets
        for index, elem in enumerate(elements):
            if elem.get("type") != "LiteralExpression":
                logger.warning(
                    "StringArrayLiteralEmitter: Non-literal expression found at index %d: %r. Using 0 as sentinel.", 
                    index, elem
                )
                # Handle non-literal expressions as null pointers or handle appropriately
                string_offsets.append(0)
                continue
            
            if elem.get("literal_type") != "string":
                logger.warning(
                    "StringArrayLiteralEmitter: Non-string literal found at index %d: %r. Using 0 as sentinel.", 
                    index, elem
                )
                # Handle non-string literals as null pointers or handle appropriately
                string_offsets.append(0)
                continue
            
            string_val = elem.get("value", "")
            logger.debug(
                "StringArrayLiteralEmitter: Storing string '%s' at index %d", 
                string_val, index
            )
            
            # Store the string in a data segment and get its memory offset
            string_offset = self.emitter._add_data_segment(string_val)
            string_offsets.append(string_offset)
            logger.debug(
                "StringArrayLiteralEmitter: String '%s' stored at memory offset %d", 
                string_val, string_offset
            )
        
        # Create the array structure: [length (4 bytes)][ptr1 (4 bytes)]...[ptrN (4 bytes)]
        logger.debug("StringArrayLiteralEmitter: Creating array structure in memory.")
        array_length_bytes = array_length.to_bytes(4, byteorder='little')  # i32 length
        array_pointers_bytes = b''.join(offset.to_bytes(4, byteorder='little') for offset in string_offsets)
        array_bytes = array_length_bytes + array_pointers_bytes
        
        for i, ptr in enumerate(string_offsets):
            logger.debug("StringArrayLiteralEmitter: Pointer %d = %d", i, ptr)
        
        # Store the array structure in memory
        array_offset = self.emitter.current_data_offset
        self.emitter.data_segments.append((array_offset, array_bytes))
        logger.debug(
            "StringArrayLiteralEmitter: Array stored at memory offset %d with %d bytes",
            array_offset, len(array_bytes)
        )
        
        # Update the current data offset
        self.emitter.current_data_offset += len(array_bytes)
        logger.debug(
            "StringArrayLiteralEmitter: Updated current_data_offset to %d", 
            self.emitter.current_data_offset
        )
        
        # Push array pointer onto stack
        out_lines.append(f"  i32.const {array_offset}")
        logger.debug(
            "StringArrayLiteralEmitter: Emitted 'i32.const %d' to reference the array.",
            array_offset
        )
