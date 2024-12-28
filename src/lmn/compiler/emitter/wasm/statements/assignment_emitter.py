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
        Example AssignmentStatement:
          {
            "type": "AssignmentStatement",
            "variable_name": "x",
            "expression": {
              "type": "LiteralExpression",
              "value": 2.718,
              "inferred_type": "f32"
            },
            "inferred_type": "f32"
          }
        """

        raw_name = node["variable_name"]
        var_name = self.controller._normalize_local_name(raw_name)

        logger.debug("emit_assignment() -> var_name=%s, assignment node=%s", var_name, node)

        # 1) expression
        expr = node.get("expression")
        expr_wasm_type = None
        if expr:
            expr_inferred = expr.get("inferred_type")
            if expr_inferred:
                expr_wasm_type = normalize_type(expr_inferred)
                logger.debug("Assignment expr has inferred_type=%s => expr_wasm_type=%s", expr_inferred, expr_wasm_type)
            else:
                expr_wasm_type = self.controller.infer_type(expr)
                logger.debug("No 'inferred_type' in expr; inferred via emitter => expr_wasm_type=%s", expr_wasm_type)

        # 2) check variable existence
        if var_name not in self.controller.func_local_map:
            raise RuntimeError(f"Variable {var_name} not declared before assignment.")

        existing_info = self.controller.func_local_map[var_name]
        existing_type = existing_info["type"]
        logger.debug("Variable '%s' existing_type=%s; expr_wasm_type=%s", var_name, existing_type, expr_wasm_type)

        # 3) unify
        if expr_wasm_type:
            final_type = unify_types(existing_type, expr_wasm_type, for_assignment=True)
            existing_info["type"] = final_type
            logger.debug("Unified var '%s' existing_type=%s with expr_wasm_type=%s => final_type=%s",
                         var_name, existing_type, expr_wasm_type, final_type)
        else:
            final_type = existing_type
            logger.debug("No expr_wasm_type; final_type remains '%s' for var '%s'", final_type, var_name)

        # 4) expression or typed zero
        if expr:
            logger.debug("Emitting expression for var '%s'...", var_name)
            self.controller.emit_expression(expr, out_lines)
        else:
            zero_instr = default_zero_for(final_type)
            logger.debug("No expression for var '%s'; pushing typed zero => %s", var_name, zero_instr)
            out_lines.append(f"  {zero_instr}")

        # 5) local.set
        set_line = f"  local.set {var_name}"
        logger.debug("Final step => %s", set_line.strip())
        out_lines.append(set_line)
