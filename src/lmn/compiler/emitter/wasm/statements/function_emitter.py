import logging

logger = logging.getLogger(__name__)

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
        Example node:
          {
            "type":  "FunctionDefinition",
            "name":  "sumFirstN",
            "params": ["n", "m"],  # plain strings for now
            "body":   [
                # e.g. { "op": "local.set", "args": ["temp"] },
                #      { "op": "local.get", "args": ["m"] }, ...
            ]
          }

        Desired WAT output:

          (func $sumFirstN (param $n i32) (param $m i32) (result i32)
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

        logger.debug(
            "emit_function() for '%s' with params=%s, body_nodes=%d",
            fname, params, len(body_nodes)
        )

        # 2) Track function name in the controller
        if fname not in self.controller.function_names:
            self.controller.function_names.append(fname)
            logger.debug("Added function '%s' to function_names: %s",
                         fname, self.controller.function_names)

        # 3) Build the function header
        param_decls = " ".join(f"(param ${p} i32)" for p in params)
        if param_decls:
            func_header = f"(func ${fname} {param_decls} (result i32)"
        else:
            func_header = f"(func ${fname} (result i32)"
        out_lines.append(func_header)
        logger.debug("Function header line: %s", func_header)

        # 4) Reset the local environment for this function
        logger.debug("Resetting func_local_map and local_counter for '%s'", fname)
        self.controller.func_local_map = {}
        self.controller.local_counter = len(params)

        # Initialize each param in func_local_map (index-based or with a type if you prefer)
        for i, p in enumerate(params):
            self.controller.func_local_map[p] = {
                "index": i,        # or just i
                "type":  "i32"     # default i32 for all params
            }
            logger.debug("Param '%s' => local index %d (i32)", p, i)

        # Collect new local variables in a fresh set
        logger.debug("Resetting new_locals set.")
        self.controller.new_locals = set()

        # 5) Emit body instructions into a temp list
        body_instructions = []
        for st_index, st_node in enumerate(body_nodes):
            logger.debug("Emitting statement %d of '%s': %s",
                         st_index, fname, st_node)
            # We call the controller's `emit_statement` method,
            # which must handle auto-registration of new locals.
            self.controller.emit_statement(st_node, body_instructions)

        # 6) Insert local declarations right after function header
        local_decl_lines = []
        for var_name in sorted(self.controller.new_locals):
            clean_var_name = self._normalize_local_name(var_name)
            declared_type = self.controller.func_local_map[var_name]["type"]
            if declared_type is None:
                # default to i32 if untyped
                declared_type = "i32"
            decl_line = f"  (local {clean_var_name} {declared_type})"
            local_decl_lines.append(decl_line)
            logger.debug("Declaring local '%s' => (local %s %s)",
                         var_name, clean_var_name, declared_type)

        insert_index = len(out_lines)
        out_lines[insert_index:insert_index] = local_decl_lines

        # 7) Append body instructions
        out_lines.extend(body_instructions)

        # 8) If no explicit return, push `0` & `return`
        out_lines.append("  i32.const 0")
        out_lines.append("  return")

        # 9) Close the function
        out_lines.append(")")
        logger.debug("Closed function '%s'.", fname)

    def _normalize_local_name(self, var_name: str) -> str:
        """
        Convert any local name that starts with '$$' into a single '$',
        or prepend '$' if it doesn't have any dollar sign at all.
        E.g.:
          'x'    -> '$x'
          '$$x'  -> '$x'
          '$x'   -> '$x'
        """
        if var_name.startswith('$$'):
            normal = '$' + var_name[2:]
        elif not var_name.startswith('$'):
            normal = f'${var_name}'
        else:
            normal = var_name

        logger.debug("_normalize_local_name: '%s' => '%s'", var_name, normal)
        return normal

