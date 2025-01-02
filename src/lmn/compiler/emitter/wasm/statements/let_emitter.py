# file: lmn/compiler/emitter/wasm/statements/let_emitter.py
import logging
from lmn.compiler.typechecker.utils import normalize_type, unify_types
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
            "expression": { "type": "LiteralExpression", "value": 3 },
            "type_annotation": "int" or None
          }
        """

        # 1) Raw name: "x"
        raw_name = node["variable"]["name"]

        annotation_str = node.get("type_annotation")
        declared_wasm_type = normalize_type(annotation_str)  # e.g. "i32", "f64", or None
        expr = node.get("expression")

        # 2) Determine type from expr if present
        expr_wasm_type = None
        if expr:
            expr_inferred = expr.get("inferred_type")
            if expr_inferred:
                expr_wasm_type = normalize_type(expr_inferred)
            else:
                expr_wasm_type = self.controller.infer_type(expr)

        # 3) Final type => unify annotation & expr type
        if declared_wasm_type or expr_wasm_type:
            final_type = declared_wasm_type or expr_wasm_type or "i32"
        else:
            final_type = None

        # 4) Insert raw_name in func_local_map if missing
        if raw_name not in self.controller.func_local_map:
            # brand new var
            self.controller.func_local_map[raw_name] = {
                "index": self.controller.local_counter,
                "type": final_type
            }
            self.controller.local_counter += 1
            self.controller.new_locals.add(raw_name)
        else:
            # unify with existing
            existing_info = self.controller.func_local_map[raw_name]
            if final_type and existing_info["type"]:
                new_type = unify_types(existing_info["type"], final_type, for_assignment=True)
                existing_info["type"] = new_type
            elif existing_info["type"] is None:
                existing_info["type"] = final_type

        # 5) Emit code
        norm_name = self.controller._normalize_local_name(raw_name)
        if expr:
            # push expr
            self.controller.emit_expression(expr, out_lines)
            out_lines.append(f"  local.set {norm_name}")
        else:
            # no init => maybe zero init
            info = self.controller.func_local_map[raw_name]
            t = info["type"]
            if t:
                zero_instr = default_zero_for(t)
                out_lines.append(f"  {zero_instr}")
                out_lines.append(f"  local.set {norm_name}")
            # else skip
