import logging

logger = logging.getLogger(__name__)

class PrintEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_print(self, node, out_lines):
        """
        Emits print instructions based on expression types, 
        supporting only newly-lowered type strings.
        """
        for ex in node["expressions"]:
            # 1) Emit code to push the expression's value on the stack
            self.controller.emit_expression(ex, out_lines)

            # 2) Figure out the final lowered type
            inferred_type = ex.get("inferred_type", "i32")
            logger.debug(f"PrintEmitter: Handling inferred_type '{inferred_type}' for expression {ex}")

            # ------- Basic numeric scalars -------
            if inferred_type == "i32":
                out_lines.append("  call $print_i32")

            elif inferred_type == "i64":
                out_lines.append("  call $print_i64")

            elif inferred_type == "f32":
                out_lines.append("  call $print_f32")

            elif inferred_type == "f64":
                out_lines.append("  call $print_f64")

            # ------- String-likes -------
            elif inferred_type == "i32_string":
                out_lines.append("  call $print_string")

            # ------- JSON-likes -------
            elif inferred_type == "i32_json":
                out_lines.append("  call $print_json")

            # ------- Arrays / Pointers -------
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
                # If you have a dedicated JSON-array print,
                # replace with `call $print_json_array`
                out_lines.append("  call $print_json")

            # ------- Fallback -------
            else:
                logger.warning(
                    f"PrintEmitter: Unknown type '{inferred_type}', defaulting to i32 printing."
                )
                out_lines.append("  call $print_i32")

            logger.debug(f"PrintEmitter: Emitting call for type '{inferred_type}'")
