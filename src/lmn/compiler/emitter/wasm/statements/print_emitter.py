import logging

logger = logging.getLogger(__name__)

class PrintEmitter:
    def __init__(self, controller):
        self.controller = controller
        self._newline_offset = None  # We'll store the "\n" data segment offset once we have it

    def emit_print(self, node, out_lines):
        """
        Emits print instructions based on expression types,
        supporting only newly-lowered type strings, plus a newline at the end.
        """

        # 1) Print each expression in the statement
        for ex in node["expressions"]:
            # (a) Emit code to push the expression's value on the stack
            self.controller.emit_expression(ex, out_lines)

            # (b) Figure out the final lowered type
            inferred_type = ex.get("inferred_type", "i32")
            logger.debug(f"PrintEmitter: Handling inferred_type '{inferred_type}' for expression {ex}")

            # (c) Dispatch to the correct "print_..." call based on inferred type
            if inferred_type == "i32":
                out_lines.append("  call $print_i32")

            elif inferred_type == "i64":
                out_lines.append("  call $print_i64")

            elif inferred_type == "f32":
                out_lines.append("  call $print_f32")

            elif inferred_type == "f64":
                out_lines.append("  call $print_f64")

            elif inferred_type == "i32_string":
                out_lines.append("  call $print_string")

            elif inferred_type == "i32_json":
                out_lines.append("  call $print_json")

            elif inferred_type == "i32_ptr":
                out_lines.append("  call $print_i32_array")

            elif inferred_type == "i64_ptr":
                out_lines.append("  call $print_i64_array")

            elif inferred_type == "f32_ptr":
                out_lines.append("  call $print_f32_array")

            elif inferred_type == "f64_ptr":
                out_lines.append("  call $print_f64_array")

            elif inferred_type == "i32_string_array":
                out_lines.append("  call $print_string_array")

            elif inferred_type == "i32_json_array":
                # If there's a dedicated JSON array print, replace with it
                out_lines.append("  call $print_json")

            else:
                logger.warning(
                    f"PrintEmitter: Unknown type '{inferred_type}', defaulting to i32 printing."
                )
                out_lines.append("  call $print_i32")

            logger.debug(f"PrintEmitter: Emitting call for type '{inferred_type}'")

        # 2) After printing all expressions in this statement, append a newline
        newline_offset = self._get_newline_offset()
        out_lines.append(f"  i32.const {newline_offset}")
        out_lines.append("  call $print_string")

    def _get_newline_offset(self):
        """
        Returns the memory offset where "\n" is stored.
        We'll store just once in a data segment so we can reuse it.
        """
        if self._newline_offset is None:
            # Add "\n" to data segments (with trailing null-terminator) so we can print it
            self._newline_offset = self.controller._add_data_segment("\n")
        return self._newline_offset
