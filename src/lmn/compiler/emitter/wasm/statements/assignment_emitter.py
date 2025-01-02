# file: lmn/compiler/emitter/wasm/statements/assignment_emitter.py
import logging
from lmn.compiler.typechecker.utils import normalize_type
from lmn.compiler.emitter.wasm.wasm_utils import default_zero_for

logger = logging.getLogger(__name__)

class AssignmentEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_assignment(self, node, out_lines):
        """
        Example AST:
        {
          "type": "AssignmentStatement",
          "variable_name": "x",
          "expression": { ... },
          "inferred_type": "i32"
        }
        """

        raw_name = node["variable_name"]
        norm_name = self.controller._normalize_local_name(raw_name)

        expr = node.get("expression")
        expr_wasm_type = None
        if expr:
            expr_inferred = expr.get("inferred_type")
            if expr_inferred:
                # 'normalize_type' typically converts "i32_string" -> "i32", etc.
                expr_wasm_type = normalize_type(expr_inferred)
            else:
                # Fallback: let the emitter guess from literal structure
                expr_wasm_type = self.controller.infer_type(expr)

        # Auto-declare the variable if missing. (Or raise error if your language disallows this.)
        if raw_name not in self.controller.func_local_map:
            self.controller.func_local_map[raw_name] = {
                "index": self.controller.local_counter,
                "type": expr_wasm_type or "i32"
            }
            self.controller.local_counter += 1
            self.controller.new_locals.add(raw_name)

        existing_info = self.controller.func_local_map[raw_name]
        existing_type = existing_info["type"]

        # --------------------------------------------------------------
        # Instead of using the typechecker's unify_types, call our WASM-level unifier.
        # (This function should be defined in your WasmEmitter, e.g. _unify_wasm_types(t1, t2))
        # --------------------------------------------------------------
        if expr_wasm_type:
            final_type = self.controller._unify_wasm_types(existing_type, expr_wasm_type)
            existing_info["type"] = final_type
        else:
            final_type = existing_type

        # 4) Emit code for the right-hand side
        if expr:
            self.controller.emit_expression(expr, out_lines)
        else:
            # No expression => zero initialize with the final type
            zero_instr = default_zero_for(final_type)
            out_lines.append(f"  {zero_instr}")

        # 5) local.set
        out_lines.append(f"  local.set {norm_name}")
