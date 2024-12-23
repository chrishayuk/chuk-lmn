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
        Example node structure:

        node = {
          "type":  "FunctionDefinition",
          "name":  "sumFirstN",
          "params": ["n", "m"],     # list of param names
          "body":   [ ... ]         # list of statements (AST)
        }

        Desired WAT output:

          (func $sumFirstN (param $n i32) (param $m i32) (result i32)
            (local $x i32)
            (local $temp i32)
            ;; body instructions...
            i32.const 0
            return
          )
        """

        # 1) Gather function info
        fname      = node["name"]
        params     = node.get("params", [])
        body_nodes = node.get("body", [])

        # 2) Track function name in the controller
        if fname not in self.controller.function_names:
            self.controller.function_names.append(fname)

        # 3) Build the function header
        param_decls = " ".join(f"(param ${p} i32)" for p in params)
        if param_decls:
            func_header = f"(func ${fname} {param_decls} (result i32)"
        else:
            func_header = f"(func ${fname} (result i32)"
        out_lines.append(func_header)

        # 4) Reset the local environment for this function
        self.controller.func_local_map = {}
        self.controller.local_counter = len(params)
        for i, p in enumerate(params):
            self.controller.func_local_map[p] = i

        # Collect new local variables in a fresh set
        self.controller.new_locals = set()

        # 5) Emit body instructions into a temp list
        body_instructions = []
        for st in body_nodes:
            self.controller.emit_statement(st, body_instructions)

        # 6) Insert local declarations after the function header, before instructions
        local_decl_lines = []
        for var_name in sorted(self.controller.new_locals):
            clean_var_name = self._normalize_local_name(var_name)
            local_decl_lines.append(f"  (local {clean_var_name} i32)")

        # Insert right after the function header
        insert_index = len(out_lines)
        out_lines[insert_index:insert_index] = local_decl_lines

        # 7) Now add body instructions
        out_lines.extend(body_instructions)

        # 8) If no explicit return, push `0` & `return`
        out_lines.append("  i32.const 0")
        out_lines.append("  return")

        # 9) Close the function
        out_lines.append(")")

    def _normalize_local_name(self, var_name: str) -> str:
        """
        Convert any local name that starts with '$$' into a single '$',
        or prepend '$' if it doesn't have any dollar sign at all.
        E.g.:
          'x'    -> '$x'
          '$$x'  -> '$x'
          '$x'   -> '$x' (unchanged)
        """
        if var_name.startswith('$$'):
            # Replace leading '$$' with single '$'
            return '$' + var_name[2:]
        elif not var_name.startswith('$'):
            # Prepend '$'
            return f'${var_name}'
        else:
            # Already starts with single '$'
            return var_name
