import logging
from lmn.compiler.emitter.wasm.wasm_utils import default_zero_for

logger = logging.getLogger(__name__)

class FunctionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is typically your main WasmEmitter or code manager that:
          - Tracks function names
          - Maintains func_local_map, local_counter
          - Has a set/dict to gather newly declared locals
          - Calls emit_statement(...) for each statement
        """
        self.controller = controller

    def emit_function(self, node, out_lines):
        """
        Example AST structure for a function node:
        {
          "type":  "FunctionDefinition",
          "name":  "sumFirstN",
          "params": [
            { "type": "FunctionParameter", "name": "n", "type_annotation": "i32_string" },
            { "type": "FunctionParameter", "name": "m", "type_annotation": "i32" }
          ],
          "return_type": "i32_string",  # or "f64" or "void", etc.
          "body": [ ...some statements... ]
        }

        The generated WAT might look like:
          (func $sumFirstN (param $n i32) (param $m i32) (result i32)
            ;; local declarations
            ;; body instructions...
            ;; fallback return if no explicit ReturnStatement
          )
        """

        fname = node["name"]
        params = node.get("params", [])
        body_nodes = node.get("body", [])

        # 1) Convert the declared return type to a valid WAT base type.
        raw_ret_type = node.get("return_type", "i32")  # fallback if not present
        ret_type = self.controller._wasm_basetype(raw_ret_type)

        logger.debug(
            "Emit function '%s' with %d params, raw_ret_type=%s => ret_type=%s",
            fname, len(params), raw_ret_type, ret_type
        )

        # 2) Track the function name for exporting
        if fname not in self.controller.function_names:
            self.controller.function_names.append(fname)

        # 3) Build the function header (params and optional (result ...))
        param_lines = []
        for p in params:
            p_name = p["name"]
            p_type = p.get("type_annotation", "i32")
            # Convert param type from custom (e.g., "i32_string") to "i32"
            wasm_param_type = self.controller._wasm_basetype(p_type)
            param_lines.append(f"(param ${p_name} {wasm_param_type})")

        param_section = " ".join(param_lines)
        func_header = f"(func ${fname}"
        if param_section:
            func_header += f" {param_section}"

        if ret_type != "void":
            func_header += f" (result {ret_type})"

        out_lines.append(func_header)
        logger.debug("Function header: %s", func_header)

        # 4) Reset local environment for this function
        self.controller.func_local_map = {}
        self.controller.local_counter = 0
        self.controller.new_locals = set()

        # 5) Put params into func_local_map, but store the *raw* type so
        #    we can keep track if we want. If you only need WAT usage, 
        #    store the converted wasm_param_type instead.
        for i, p in enumerate(params):
            p_name = p["name"]
            raw_p_type = p.get("type_annotation", "i32")
            self.controller.func_local_map[p_name] = {
                "index": i,
                "type":  raw_p_type  # or wasm_param_type, depending on your needs
            }
            self.controller.local_counter += 1

        # 6) Emit the body statements
        body_instructions = []
        encountered_return = False

        for stmt in body_nodes:
            stmt_type = stmt.get("type")
            if stmt_type == "ReturnStatement":
                encountered_return = True

            # Always emit the statement via controller
            self.controller.emit_statement(stmt, body_instructions)

        # 7) Insert local declarations for newly referenced variables.
        #    If a var isn't in func_local_map yet, we auto-declare it as "i32".
        local_decl_lines = []
        for var_name in sorted(self.controller.new_locals):
            if var_name not in self.controller.func_local_map:
                idx = self.controller.local_counter
                self.controller.func_local_map[var_name] = {
                    "index": idx,
                    "type": "i32"  # fallback type if unknown
                }
                self.controller.local_counter += 1

            normalized = self._normalize_local_name(var_name)
            local_type = self.controller.func_local_map[var_name].get("type", "i32")

            # Convert local_type from e.g. "i32_string" to "i32"
            wasm_local_type = self.controller._wasm_basetype(local_type)
            local_decl_lines.append(f"  (local {normalized} {wasm_local_type})")

        # Insert them right after the function header
        insert_index = len(out_lines)
        for decl in reversed(local_decl_lines):
            out_lines.insert(insert_index, decl)

        # 8) Add the actual body instructions
        out_lines.extend(body_instructions)

        # 9) If no explicit return => push typed 0, then return
        if not encountered_return:
            zero_instr = default_zero_for(ret_type)
            if zero_instr:  # If ret_type != "void"
                out_lines.append(f"  {zero_instr}")
            out_lines.append("  return")

        # 10) Close the function
        out_lines.append(")")
        logger.debug("Finished function '%s'.", fname)

    def _normalize_local_name(self, var_name: str) -> str:
        """
        Ensures local var has one '$' prefix:
          'x'   -> '$x'
          '$$x' -> '$x'
          '$x'  -> '$x'
        """
        if var_name.startswith('$$'):
            return '$' + var_name[2:]
        elif not var_name.startswith('$'):
            return f'${var_name}'
        else:
            return var_name
