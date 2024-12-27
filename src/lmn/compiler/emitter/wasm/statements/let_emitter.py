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
        node example:
        {
          "type": "LetStatement",
          "variable": { "type": "VariableExpression", "name": "z" },
          "expression": { "type": "LiteralExpression", "value": 100 },
          "type_annotation": "int.32" or None,
        }

        Steps:
         1) Get var_name + optional type_annotation => e.g. "i32"
         2) If expression => get expr type (from 'inferred_type' or controller.infer_type)
         3) final_type = unify(declared, expr) or "i32" if neither
         4) If brand-new var => adopt final_type w/o unify w/existing type.
            If existing => unify w/existing => can auto-promote if needed.
         5) Emit expression or default-zero => local.set $var
        """

        # 1) variable name + optional annotation
        raw_name = node["variable"]["name"]
        var_name = self.controller._normalize_local_name(raw_name)

        annotation_str = node.get("type_annotation")
        declared_wasm_type = normalize_type(annotation_str)  # e.g. "i32" or "i64"

        # 2) expression type
        expr = node.get("expression")
        expr_wasm_type = None
        if expr is not None:
            expr_inferred = expr.get("inferred_type")
            if expr_inferred is not None:
                # If the AST already has 'inferred_type', use that
                expr_wasm_type = normalize_type(expr_inferred)
            else:
                # Otherwise, let the controller (mock) infer the type
                expr_wasm_type = self.controller.infer_type(expr)

        # 3) unify => if we have declared + expr => unify, else fallback
        final_type = declared_wasm_type or expr_wasm_type or "i32"

        # 4) handle new vs existing
        if var_name not in self.controller.func_local_map:
            # brand-new variable => no existing type to unify with
            # if we do have both declared & expr => unify them
            if declared_wasm_type and expr_wasm_type:
                final_type = unify_types(declared_wasm_type, expr_wasm_type, for_assignment=True)

            # store final_type in the local map
            self.controller.func_local_map[var_name] = {
                "index": self.controller.local_counter,
                "type": final_type
            }
            self.controller.local_counter += 1
            self.controller.new_locals.add(var_name)

        else:
            # existing var => unify existing type w/ the new expr
            existing_info = self.controller.func_local_map[var_name]
            existing_type = existing_info["type"]

            if expr_wasm_type:
                final_type = unify_types(existing_type, expr_wasm_type, for_assignment=True)
                existing_info["type"] = final_type
            else:
                final_type = existing_type

            # Also unify declared type if present
            if declared_wasm_type and declared_wasm_type != final_type:
                final_type = unify_types(declared_wasm_type, final_type, for_assignment=True)
                existing_info["type"] = final_type

        # 5) Emit expression or default-zero => local.set
        if expr is not None:
            self.controller.emit_expression(expr, out_lines)
        else:
            zero_instr = default_zero_for(final_type)
            out_lines.append(f"  {zero_instr}")

        out_lines.append(f"  local.set {var_name}")
