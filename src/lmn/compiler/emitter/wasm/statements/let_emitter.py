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
        """
        raw_name = node["variable"]["name"]

        # e.g., user wrote: `let x: double = 0.8`
        annotation_str = node.get("type_annotation")
        declared_wasm_type = normalize_type(annotation_str)  # e.g. "f64" if user annotated

        expr = node.get("expression")

        # ---------------------------------------------------------------------
        # 1) Determine the expression's type
        # ---------------------------------------------------------------------
        expr_wasm_type = None
        if expr:
            expr_inferred = expr.get("inferred_type")  # e.g. "f64", "i32_string", etc.
            if expr_inferred:
                # e.g. "f64" => becomes "f64", "i32_string" => "i32"
                expr_wasm_type = normalize_type(expr_inferred)
            else:
                # If there's no 'inferred_type', do a simple fallback
                expr_wasm_type = self.controller.infer_type(expr)
        # else no expression => variable declared but no initializer

        # ---------------------------------------------------------------------
        # 2) Final type => unify declared and expression type, fallback to i32
        # ---------------------------------------------------------------------
        if declared_wasm_type or expr_wasm_type:
            final_type = declared_wasm_type or expr_wasm_type or "i32"
        else:
            final_type = None

        # ---------------------------------------------------------------------
        # 3) Insert or unify the variable in func_local_map
        # ---------------------------------------------------------------------
        if raw_name not in self.controller.func_local_map:
            # brand new var
            self.controller.func_local_map[raw_name] = {
                "index": self.controller.local_counter,
                "type": final_type
            }
            self.controller.local_counter += 1
            self.controller.new_locals.add(raw_name)
        else:
            # unify with existing if we already had a type
            existing_info = self.controller.func_local_map[raw_name]
            if final_type and existing_info["type"]:
                # -- Use WASM-level unifier instead of typechecker's unify_types --
                new_type = self.controller._unify_wasm_types(existing_info["type"], final_type)
                existing_info["type"] = new_type
            elif existing_info["type"] is None:
                existing_info["type"] = final_type

        # ---------------------------------------------------------------------
        # 4) Emit code to initialize the variable
        # ---------------------------------------------------------------------
        norm_name = self.controller._normalize_local_name(raw_name)
        if expr:
            # push expr onto stack
            self.controller.emit_expression(expr, out_lines)
            # store in local
            out_lines.append(f"  local.set {norm_name}")
        else:
            # no initializer => zero-init if we have a known type
            info = self.controller.func_local_map[raw_name]
            t = info["type"]
            if t:
                zero_instr = default_zero_for(t)
                if zero_instr:
                    out_lines.append(f"  {zero_instr}")
                    out_lines.append(f"  local.set {norm_name}")
