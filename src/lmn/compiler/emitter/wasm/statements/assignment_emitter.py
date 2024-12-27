# file: lmn/compiler/emitter/wasm/statements/assignment_emitter.py

import logging
from lmn.compiler.typechecker.utils import normalize_type, unify_types

# logger
logger = logging.getLogger(__name__)

class AssignmentEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_assignment(self, node, out_lines):
        """
        node example:
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

        Steps:
         1) Confirm the variable is already declared (in func_local_map).
         2) Get expression type from 'inferred_type' (or via controller.infer_type).
         3) Unify it with the existing local type, updating the local map if needed.
         4) Emit code for the expression.
         5) local.set $var_name
        """

        # 1) variable name
        raw_name = node["variable_name"]
        var_name = self.controller._normalize_local_name(raw_name)

        # 2) expression
        expr = node["expression"]
        # Attempt to read its 'inferred_type' from the AST first
        expr_wasm_type = None
        if expr is not None:
            expr_type = expr.get("inferred_type")
            if expr_type:
                expr_wasm_type = normalize_type(expr_type)
            else:
                expr_wasm_type = self.controller.infer_type(expr)

        # 3) Ensure the variable already exists in func_local_map
        if var_name not in self.controller.func_local_map:
            # This indicates the AST or symbol table is out of sync
            raise RuntimeError(f"Variable {var_name} not declared before assignment.")

        existing_info = self.controller.func_local_map[var_name]
        existing_type = existing_info["type"]

        # unify if we have an expression type
        if expr_wasm_type:
            final_type = unify_types(existing_type, expr_wasm_type, for_assignment=True)
            # update the type in local map in case there's a promotion
            existing_info["type"] = final_type
        else:
            # No expression type => fallback to existing
            final_type = existing_type

        # 4) Emit the expression code
        if expr is not None:
            self.controller.emit_expression(expr, out_lines)
        else:
            # Edge case: "x = ???" with no expression is unusual
            # You might want to raise an error or push a default
            out_lines.append("  i32.const 0")  # or some default

        # 5) local.set
        out_lines.append(f"  local.set {var_name}")
