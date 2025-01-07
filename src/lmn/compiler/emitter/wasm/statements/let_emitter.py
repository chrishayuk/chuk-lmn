# file: lmn/compiler/emitter/wasm/statements/let_emitter.py
import logging
from lmn.compiler.typechecker.utils import normalize_type
from lmn.compiler.emitter.wasm.wasm_utils import default_zero_for

logger = logging.getLogger(__name__)

class LetEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_let(self, node, out_lines):
        """
        Example LetStatement node:
          {
            "type": "LetStatement",
            "variable": { "type": "VariableExpression", "name": "x" },
            "expression": { 
              "type": "LiteralExpression", 
              "value": 0.8,
              "inferred_type": "f64"
            },
            "type_annotation": None
          }

        We'll handle two special cases:
          1) let sum_func = function(a, b) ...
             => Lift to an actual top-level function "anon_X" + set alias sum_func->anon_X
          2) let sum_func_alias = someFunction
             => If that 'someFunction' is known or we want a direct alias,
                set sum_func_alias->someFunction
        Otherwise, we do normal "local" creation & initialization.
        """
        raw_name = node["variable"]["name"]

        # e.g., user wrote: `let x: double = 0.8`
        annotation_str = node.get("type_annotation")
        declared_wasm_type = normalize_type(annotation_str)

        expr = node.get("expression")

        #######################################################################
        # CASE 1) The expression is an "anonymous function"
        #######################################################################
        if expr and expr["type"] == "FnExpression" and not expr.get("name"):
            # 1) Create a fresh function name, e.g. "anon_0"
            new_func_name = f'anon_{self.controller.function_counter}'
            self.controller.function_counter += 1

            # 2) Build a pseudo "FunctionDefinition" node 
            #    so we can reuse your existing function emitter
            func_def_node = {
                "type": "FunctionDefinition",
                "name": new_func_name,
                "params": expr.get("parameters", []),
                "body": expr.get("body", []),
                # If your AST has a "return_type" on FnExpression, pass it here
                "return_type": expr.get("return_type")
            }

            # 3) Emit the new top-level function
            func_lines = []
            self.controller.function_emitter.emit_function(func_def_node, func_lines)
            self.controller.functions.append(func_lines)
            self.controller.function_names.append(new_func_name)

            # 4) Record an alias so that "sum_func" => "anon_0"
            self.controller.func_alias_map[raw_name] = new_func_name

            # 5) Do NOT emit a local i32 for this; we skip normal logic
            return

        #######################################################################
        # CASE 2) The expression is a "VariableExpression"
        #   e.g. let sum_func_alias = add
        #######################################################################
        if expr and expr["type"] == "VariableExpression":
            aliased_name = expr["name"]  # e.g. "add"
            # Optional: we could check if 'aliased_name' is in function_names, or just alias
            self.controller.func_alias_map[raw_name] = aliased_name
            # Do NOT emit a local for it, skip normal logic
            return

        #######################################################################
        # Otherwise, proceed as normal numeric/string let logic
        #######################################################################

        # 1) Determine expression's type
        expr_wasm_type = None
        if expr:
            expr_inferred = expr.get("inferred_type")
            if expr_inferred:
                expr_wasm_type = normalize_type(expr_inferred)
            else:
                expr_wasm_type = self.controller.infer_type(expr)

        # 2) Final type => unify declared and expression type, fallback "i32"
        if declared_wasm_type or expr_wasm_type:
            final_type = declared_wasm_type or expr_wasm_type or "i32"
        else:
            final_type = None

        # 3) Insert / unify the variable in func_local_map
        if raw_name not in self.controller.func_local_map:
            self.controller.func_local_map[raw_name] = {
                "index": self.controller.local_counter,
                "type": final_type
            }
            self.controller.local_counter += 1
            self.controller.new_locals.add(raw_name)
        else:
            existing_info = self.controller.func_local_map[raw_name]
            if final_type and existing_info["type"]:
                new_type = self.controller._unify_wasm_types(existing_info["type"], final_type)
                existing_info["type"] = new_type
            elif existing_info["type"] is None:
                existing_info["type"] = final_type

        # 4) Emit code to initialize the variable (if any)
        norm_name = self.controller._normalize_local_name(raw_name)
        if expr:
            # push expr onto stack
            self.controller.emit_expression(expr, out_lines)
            # store in local
            out_lines.append(f"  local.set {norm_name}")
        else:
            # zero-init if we have a known type
            info = self.controller.func_local_map[raw_name]
            t = info["type"]
            if t:
                zero_instr = default_zero_for(t)
                if zero_instr:
                    out_lines.append(f"  {zero_instr}")
                    out_lines.append(f"  local.set {norm_name}")
