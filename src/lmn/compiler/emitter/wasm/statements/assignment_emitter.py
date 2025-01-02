# file: lmn/compiler/emitter/wasm/statements/assignment_emitter.py
import logging
from lmn.compiler.typechecker.utils import normalize_type, unify_types
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
                expr_wasm_type = normalize_type(expr_inferred)
            else:
                expr_wasm_type = self.controller.infer_type(expr)

        # If x is not in func_local_map => either auto-declare or raise error
        if raw_name not in self.controller.func_local_map:
            # If your language requires a let statement, raise:
            # raise RuntimeError(f"Var '{raw_name}' not declared.")
            # Otherwise, auto-declare:
            self.controller.func_local_map[raw_name] = {
                "index": self.controller.local_counter,
                "type": expr_wasm_type or "i32"
            }
            self.controller.local_counter += 1
            self.controller.new_locals.add(raw_name)

        existing_info = self.controller.func_local_map[raw_name]
        existing_type = existing_info["type"]

        # unify
        if expr_wasm_type:
            final_type = unify_types(existing_type, expr_wasm_type, for_assignment=True)
            existing_info["type"] = final_type
        else:
            final_type = existing_type

        # Emit expression or zero
        if expr:
            self.controller.emit_expression(expr, out_lines)
        else:
            zero_instr = default_zero_for(final_type)
            out_lines.append(f"  {zero_instr}")

        out_lines.append(f"  local.set {norm_name}")
