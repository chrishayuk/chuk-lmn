# compiler/emitter/wasm/statements/function_emitter.py

class FunctionEmitter:
    def __init__(self, controller):
        """
        The controller is typically your main WasmEmitter or code manager that:
          - Tracks function names
          - Maintains func_local_map, local_counter
          - Has a set/dict to gather newly declared locals from sub-emitters
          - Calls emit_statement(...) for each statement
        """
        self.controller = controller

    def emit_function(self, node, out_lines):
        """
        node = {
          "type": "FunctionDefinition",
          "name":  "sumFirstN",
          "params": ["n", ...],
          "body":   [ ... statement nodes ... ]
        }

        We'll produce something like:
          (func $sumFirstN (param $n i32) (param $m i32) (result i32)
            (local $x i32)
            (local $temp i32)
            ;; body instructions
            i32.const 0
            return
          )
        """
        # 1) Gather function info
        fname = node["name"]
        params = node["params"]  # list of param names
        body_nodes = node["body"]

        # 2) Track function name in the controller
        if fname not in self.controller.function_names:
            self.controller.function_names.append(fname)

        # 3) Build the function header
        #    e.g., (param $n i32) for each param
        param_decls = " ".join(f"(param ${p} i32)" for p in params)
        if param_decls:
            func_header = f'(func ${fname} {param_decls} (result i32)'
        else:
            func_header = f'(func ${fname} (result i32'
        out_lines.append(func_header)

        # 4) Reset the local map & counters for this function
        self.controller.func_local_map = {}
        self.controller.local_counter = len(params)

        # Map each param name => local index
        for i, p in enumerate(params):
            self.controller.func_local_map[p] = i

        # Also reset a data structure to collect newly declared local variables
        # from sub-emitters (like SetEmitter, etc.)
        self.controller.new_locals = set()

        # 5) Emit each statement in the body
        for st in body_nodes:
            self.controller.emit_statement(st, out_lines)

        # 6) Insert local declarations for new variables
        #    We'll do it right after the function header line for standard WAT
        local_decl_lines = []
        for var_name in sorted(self.controller.new_locals):
            local_decl_lines.append(f'  (local ${var_name} i32)')

        # Insert them right after the function header (the last line we appended)
        if local_decl_lines:
            # The function header is at the end of out_lines, so insert after it
            insert_index = len(out_lines)
            # We insert them there, so they appear immediately after
            out_lines[insert_index:insert_index] = local_decl_lines

        # 7) If no explicit return was encountered, push default 0 & return
        out_lines.append('  i32.const 0')
        out_lines.append('  return')

        # 8) End the function
        out_lines.append(')')

