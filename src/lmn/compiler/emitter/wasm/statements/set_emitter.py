# lmn/compiler/emitter/wasm/statements/set_emitter.py
from lmn.compiler.typechecker.utils import normalize_type, unify_types
from lmn.compiler.emitter.wasm.wasm_utils import default_zero_for

class SetEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_set(self, node, out_lines):
        """
        node e.g.:
        {
          "type": "SetStatement",
          "variable": { "type": "VariableExpression", "name": "dbl", "inferred_type": "f64" },
          "expression": {...} or null,
          "type_annotation": "float.64" or null
        }

        We'll:
          1) Map type_annotation => "f32","f64","i32","i64" if present
          2) If no variable declared yet, unify or set local type
          3) If expression is None => default-init to zero
             else emit the expression
          4) local.set $var
        """

        # Step 1: variable name + annotation
        var_name = node["variable"]["name"]
        var_name = self.controller._normalize_local_name(var_name)
        annotation_str = node.get("type_annotation", None)
        declared_wasm_type = normalize_type(annotation_str)  # e.g. "f64" from "float.64"

        # Step 2: If we have an expression, we can figure out its type
        expr = node.get("expression")
        expr_wasm_type = None
        if expr is not None:
            # Possibly your emitter has a "infer_expr_type" or 
            # you rely on "inferred_type" from the AST
            # For simplicity, let's see if "inferred_type" is in the node
            expr_inferred = expr.get("inferred_type")
            expr_wasm_type = normalize_type(expr_inferred)  # e.g. "f64"
            # If you lack "inferred_type", you might do: expr_wasm_type = self.controller.infer_type(expr)

        # Step 3: Determine the final local type
        final_type = declared_wasm_type or expr_wasm_type or "i32"

        # If we already have a known local type from previous usage, unify
        if var_name not in self.controller.func_local_map:
            # This is the first time we see 'var_name'
            # unify if we have both declared_wasm_type + expr_wasm_type
            if declared_wasm_type and expr_wasm_type:
                # unify for assignment => final_type is unify_types(declared, expr, for_assignment=True)
                final_type = unify_types(declared_wasm_type, expr_wasm_type, for_assignment=True)
            # Or if we have only one, final_type is whichever is non-None
            # If both are None => "i32" is fallback

            index = self.controller.local_counter
            self.controller.local_counter += 1
            self.controller.func_local_map[var_name] = {
                "index": index,
                "type": final_type
            }
            self.controller.new_locals.add(var_name)
        else:
            # variable previously declared
            existing_info = self.controller.func_local_map[var_name]
            existing_type = existing_info["type"]  # e.g. "f32"

            if expr_wasm_type:
                # unify existing_type with expr_wasm_type
                final_type = unify_types(existing_type, expr_wasm_type, for_assignment=True)
                existing_info["type"] = final_type
            else:
                # no expression => remain at existing_type
                final_type = existing_type

            if declared_wasm_type and declared_wasm_type != final_type:
                # unify with declared if needed
                final_type = unify_types(declared_wasm_type, final_type, for_assignment=True)
                existing_info["type"] = final_type

        # Step 4: Emit code
        if expr is not None:
            # We have an expression => generate code for it
            self.controller.emit_expression(expr, out_lines)  
            out_lines.append(f'  local.set {var_name}')
        else:
            # No expression => default-initialize to 0
            zero_instr = default_zero_for(final_type)
            out_lines.append(f'  {zero_instr}')
            out_lines.append(f'  local.set {var_name}')
