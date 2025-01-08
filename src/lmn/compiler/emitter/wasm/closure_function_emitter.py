# file: lmn/compiler/emitter/wasm/closure_function_emitter.py

import logging
logger = logging.getLogger(__name__)

class ClosureFunctionEmitter:
    """
    Dynamically emits a closure function in a style similar
    to your existing FunctionEmitter, but specialized for closures
    that capture variables.

    It expects:
      - self.controller: typically your main WasmEmitter or a subset,
                         giving access to:
         * self.controller.function_names
         * self.controller.functions
         * self.controller._wasm_basetype(...) 
         * self.controller._normalize_local_name(...)
         * your environment/table managers, e.g. self.controller.closure_table
           or self.controller.closure_runtime
      - The closure AST node: something like
         {
           "type": "AnonymousFunction",
           "parameters": [...],
           "body": [...],
           "return_type": "int",
           "captures": ["x", "z"]   # if you track captured vars
         }
    """

    def __init__(self, controller):
        """
        :param controller: A reference to your main WasmEmitter or a sub-emitter
        """
        self.controller = controller

    def emit_closure_function(self, closure_node, closure_id, environment_layout):
        """
        Produces lines for a new closure function:
          (func $closure_fn_{closure_id} (type $some_closure_type)
            (param i32) ...  ; environment pointer
            (param y i32) ...
            (result i32)
            ...
          )

        :param closure_node: The AST for this inline closure, e.g.
            {
              "type": "AnonymousFunction",
              "parameters": [["y","int"]],
              "body": [...],
              "return_type": "int",
              "captures": ["x"]
            }
        :param closure_id: a unique integer used to name the function,
                           e.g. "closure_fn_5" => $closure_fn_5
        :param environment_layout: a dict or list describing how captures
                                   are laid out in memory. For instance:
                                   { "x":0, "z":4 } meaning x is at offset 0,
                                   z at offset 4, etc.

        :return: the function name we generated, e.g. "closure_fn_5"
        """

        # 1) Construct a function name
        func_name = f"closure_fn_{closure_id}"

        if func_name not in self.controller.function_names:
            self.controller.function_names.append(func_name)

        # 2) We'll produce lines for a new function definition
        #    Typically we have (param $env i32) plus user-level params
        #    Then we unify them with your table function type, e.g. (type $closure_type).
        lines = []
        lines.append(f"(func ${func_name} (type $closure_type)")

        # Our first param is environment pointer => (param $env i32)
        param_decl = ["(param $env i32)"]
        
        # Then for each user-level param in closure_node["parameters"]
        # we do e.g. (param $pName i32/f64 etc.)
        user_params = closure_node.get("parameters", [])
        # user_params might be a list of [("y", "int")] or a list of dicts
        # We'll adapt to your style:
        for i, p in enumerate(user_params):
            # If p is a tuple/list => (paramName, paramType)
            if isinstance(p, (list, tuple)):
                p_name, p_type = p
            else:
                p_name = p["name"]
                p_type = p.get("type_annotation", "int")

            wasm_type = self.controller._wasm_basetype(p_type)
            norm_p_name = self.controller._normalize_local_name(p_name)
            param_decl.append(f"(param {norm_p_name} {wasm_type})")

        # Return type
        raw_ret_type = closure_node.get("return_type", "int")
        ret_wasm_type = self.controller._wasm_basetype(raw_ret_type)

        # Build function signature line
        sig_line = " ".join(param_decl)
        if ret_wasm_type != "void":
            lines[-1] += f" {sig_line} (result {ret_wasm_type})"
        else:
            lines[-1] += f" {sig_line}"

        # If you'd prefer to do local declarations, you can do them below
        # For now, we handle them similarly to your FunctionEmitter steps.
        
        # 3) Translate the body. We need to interpret closure_node["body"],
        #    but references to captured variables => "local.get $env" + "i32.load offset=..."
        #    references to user param => "local.get $pName"
        # In a real design, you'd parse the AST recursively. For demonstration:
        lines.append("  ;; Emitting closure body instructions...")

        # If we track "captures", let's say closure_node["captures"] = ["x", "z"]
        # environment_layout might be {"x":0, "z":4}
        
        # We'll do a naive approach: if the body is something like
        # ReturnStatement => "x + y"
        # We'll just inline i32.load for x, local.get for y, etc.
        # We won't do a full AST traversal, but demonstrate the concept.
        
        body = closure_node.get("body", [])
        # Example: a single ReturnStatement with a BinaryExpression
        # We'll just do a naive check:
        if len(body) == 1 and body[0].get("type") == "ReturnStatement":
            expr = body[0].get("expression")
            if expr and expr.get("type") == "BinaryExpression":
                left = expr.get("left")
                right = expr.get("right")
                # If left is captured var 'x', do i32.load
                # If right is param 'y', do local.get $y
                # Then i32.add => return
                lines.append("  ;; naive closure body for x + y example")
                # For 'x'
                if left["type"] == "VariableExpression" and left["name"] in environment_layout:
                    # load from env
                    offset = environment_layout[left["name"]]
                    lines.append("  local.get $env")
                    lines.append(f"  i32.load offset={offset}") 
                else:
                    # fallback
                    lines.append("  i32.const 0")

                # For 'y'
                if right["type"] == "VariableExpression":
                    param_name = right["name"]  # e.g. "y"
                    # We must figure out the param index => or just do local.get $y
                    # We'll assume the user param is named "y" => "local.get $y"
                    norm_p_name = self.controller._normalize_local_name(param_name)
                    lines.append(f"  local.get {norm_p_name}")
                else:
                    lines.append("  i32.const 0")

                lines.append("  i32.add")
                lines.append("  return")
            else:
                lines.append("  ;; fallback => i32.const 0, return")
                lines.append("  i32.const 0")
                lines.append("  return")
        else:
            lines.append("  ;; fallback => i32.const 0, return")
            lines.append("  i32.const 0")
            lines.append("  return")

        # 4) Close function
        lines.append(")")

        # 5) Append lines to your final output
        self.controller.functions.append(lines)
        logger.debug("ClosureFunctionEmitter: emitted closure function '%s'", func_name)
        
        return func_name
