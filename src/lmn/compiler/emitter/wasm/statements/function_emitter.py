# file: lmn/compiler/emitter/wasm/statements/function_emitter.py
import logging
from lmn.compiler.emitter.wasm.wasm_utils import default_zero_for

logger = logging.getLogger(__name__)

class FunctionEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_function(self, node, out_lines):
        fname = node["name"]
        params = node.get("params", [])
        body_nodes = node.get("body", [])

        # 1) Return type
        raw_ret_type = node.get("return_type", "i32")
        ret_type = self.controller._wasm_basetype(raw_ret_type)

        if fname not in self.controller.function_names:
            self.controller.function_names.append(fname)

        # 2) Build function header
        param_lines = []
        for p in params:
            p_name = p["name"]
            p_type = p.get("type_annotation", "i32")
            wasm_param_type = self.controller._wasm_basetype(p_type)
            norm_p_name = self._normalize_local_name(p_name)
            param_lines.append(f"(param {norm_p_name} {wasm_param_type})")

        param_section = " ".join(param_lines)
        func_header = f"(func ${fname}"
        if param_section:
            func_header += f" {param_section}"

        if ret_type != "void":
            func_header += f" (result {ret_type})"

        out_lines.append(func_header)

        # 3) Clear function environment
        self.controller.func_local_map = {}
        self.controller.local_counter = 0
        self.controller.new_locals = set()

        # 4) Store params in func_local_map
        for i, p in enumerate(params):
            p_name = p["name"]
            raw_p_type = p.get("type_annotation", "i32")
            self.controller.func_local_map[p_name] = {
                "index": i,
                "type":  raw_p_type
            }
            self.controller.local_counter += 1

        # 5) Emit body statements
        body_instructions = []
        encountered_return = False
        for stmt in body_nodes:
            if stmt.get("type") == "ReturnStatement":
                encountered_return = True
            self.controller.emit_statement(stmt, body_instructions)

        # 6) Insert local declarations for new variables
        local_decl_lines = []
        for var_name in sorted(self.controller.new_locals):
            if var_name not in self.controller.func_local_map:
                # fallback to i32
                self.controller.func_local_map[var_name] = {
                    "index": self.controller.local_counter,
                    "type": "i32"
                }
                self.controller.local_counter += 1

            norm_name = self._normalize_local_name(var_name)
            local_type = self.controller.func_local_map[var_name].get("type", "i32")
            wasm_local_type = self.controller._wasm_basetype(local_type)
            local_decl_lines.append(f"  (local {norm_name} {wasm_local_type})")

        # Insert local declarations after func header
        insert_index = len(out_lines)
        for decl in reversed(local_decl_lines):
            out_lines.insert(insert_index, decl)

        # 7) Add body
        out_lines.extend(body_instructions)

        # 8) Fallback return if needed
        if not encountered_return:
            zero_instr = default_zero_for(ret_type)
            if zero_instr:
                out_lines.append(f"  {zero_instr}")
            out_lines.append("  return")

        out_lines.append(")")

    def _normalize_local_name(self, var_name: str) -> str:
        if var_name.startswith('$$'):
            return '$' + var_name[2:]
        elif not var_name.startswith('$'):
            return f'${var_name}'
        else:
            return var_name
