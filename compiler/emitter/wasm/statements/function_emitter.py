# compiler/emitter/wasm/statements/function_emitter.py

class FunctionEmitter:
    def __init__(self, controller):
        """
        The controller is typically your main WasmEmitter or some manager that:
          - tracks function names
          - tracks locals
          - can dispatch to emit_statement(...)
        """
        self.controller = controller

    def emit_function(self, node, out_lines):
        """
        node example:
          {
            "type": "FunctionDefinition",
            "name": "sumFirstN",
            "params": ["n"],
            "body": [ ... statement nodes ... ]
          }
        We'll generate lines for a WASM function definition, e.g.:
          (func $sumFirstN (param i32) (result i32)
             ...body...
             i32.const 0
             return
          )
        """

        # 1) Gather function info
        fname = node["name"]
        params = node["params"]  # list of param names
        body_nodes = node["body"]

        # 2) Track function name in the controller (for exporting or referencing)
        self.controller.function_names.append(fname)

        # 3) Build the function signature
        #    e.g., (param i32) for each param
        param_decls = " ".join("(param i32)" for _ in params)

        # Example function header:
        #   (func $fname (param i32) (param i32) (result i32)
        # or if there are no params:
        #   (func $fname (result i32)
        if param_decls:
            func_header = f'(func ${fname} {param_decls} (result i32)'
        else:
            func_header = f'(func ${fname} (result i32'

        out_lines.append(func_header)

        # 4) Reset local environment for this function
        self.controller.func_local_map = {}
        self.controller.local_counter = len(params)

        # Map each param name -> local index
        for i, p in enumerate(params):
            self.controller.func_local_map[p] = i

        # 5) Emit each statement in the body
        for st in body_nodes:
            self.controller.emit_statement(st, out_lines)

        # 6) If no explicit return was encountered, push default 0 & return
        out_lines.append('  i32.const 0')
        out_lines.append('  return')

        # 7) End the function
        out_lines.append(')')

