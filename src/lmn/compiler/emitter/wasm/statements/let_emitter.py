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
        Example 'LetStatement' node:
          {
            "type": "LetStatement",
            "variable": { "type": "VariableExpression", "name": "z" },
            "expression": { "type": "LiteralExpression", "value": 100 },
            "type_annotation": "int" or None,
          }
        """

        raw_name = node["variable"]["name"]
        var_name = self.controller._normalize_local_name(raw_name)

        annotation_str = node.get("type_annotation")
        declared_wasm_type = normalize_type(annotation_str)  # e.g. "i32", "i64", "f32", "f64" or None
        expr = node.get("expression")

        logger.debug(
            "emit_let() -> var_name=%s, annotation_str=%s => declared_wasm_type=%s, node=%s",
            var_name, annotation_str, declared_wasm_type, node
        )

        # 1) Determine expression wasm type if there's an initializer
        expr_wasm_type = None
        if expr:
            expr_inferred = expr.get("inferred_type")
            if expr_inferred:
                expr_wasm_type = normalize_type(expr_inferred)
                logger.debug(
                    "LetStatement: expression has inferred_type=%s => expr_wasm_type=%s",
                    expr_inferred, expr_wasm_type
                )
            else:
                expr_wasm_type = self.controller.infer_type(expr)
                logger.debug(
                    "LetStatement: expression lacks 'inferred_type'; naive inference => expr_wasm_type=%s",
                    expr_wasm_type
                )

        # 2) If we have declared + expr => unify, else fallback "i32" if needed.
        #    BUT if there's *no* annotation and *no* expression, we let final_type be None,
        #    so we skip pushing a default zero. We'll finalize it on first assignment.
        if declared_wasm_type or expr_wasm_type:
            # We do have some info => unify or fallback i32
            final_type = declared_wasm_type or expr_wasm_type or "i32"
            logger.debug(
                "LetStatement unify step => declared_wasm_type=%s, expr_wasm_type=%s => final_type=%s",
                declared_wasm_type, expr_wasm_type, final_type
            )
        else:
            # Means no annotation, no expression => skip zero init
            final_type = None
            logger.debug(
                "No annotation & no expression => final_type=None => skip pushing zero for var '%s'",
                var_name
            )

        # 3) handle new vs existing local
        if var_name not in self.controller.func_local_map:
            logger.debug("Variable '%s' is new => storing final_type=%s", var_name, final_type)
            self.controller.func_local_map[var_name] = {
                "index": self.controller.local_counter,
                "type": final_type,  # might be None
            }
            self.controller.local_counter += 1
            self.controller.new_locals.add(var_name)
        else:
            logger.debug("Variable '%s' already exists => unify with existing...", var_name)
            existing_info = self.controller.func_local_map[var_name]
            existing_type = existing_info["type"]

            if final_type is not None and existing_type is not None:
                # unify
                unified = unify_types(existing_type, final_type, for_assignment=True)
                existing_info["type"] = unified
                logger.debug(
                    "Existing type=%s unify with new final=%s => unified=%s",
                    existing_type, final_type, unified
                )
            elif existing_type is None:
                # if existing was None and we have a final_type => store it
                existing_info["type"] = final_type
                logger.debug(
                    "Existing type=None => store final_type=%s for var=%s",
                    final_type, var_name
                )
            # else final_type is None => skip

        # 4) If there's an initializer expression, emit it; else push typed zero if final_type is known.
        if expr:
            logger.debug("Emitting initializer expression for var '%s' => final_type=%s", var_name, final_type)
            self.controller.emit_expression(expr, out_lines)
            out_lines.append(f"  local.set {var_name}")
        else:
            # no expression
            if final_type:
                # if we do have a final type (e.g. from annotation), push typed zero
                zero_instr = default_zero_for(final_type)
                logger.debug(
                    "No initializer => pushing typed zero for '%s' => %s (final_type=%s)",
                    var_name, zero_instr, final_type
                )
                out_lines.append(f"  {zero_instr}")
                out_lines.append(f"  local.set {var_name}")
            else:
                # final_type is None => skip entirely (no zero init)
                logger.debug(
                    "No initializer & final_type=None => skip any code for var '%s' now. Will unify on first assignment.",
                    var_name
                )
