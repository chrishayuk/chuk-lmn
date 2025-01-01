# file: lmn/compiler/emitter/wasm/expressions/postfix_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class PostfixExpressionEmitter:
    """
    Handles postfix operators ('++' / '--') on numeric types in WASM.
    e.g. a++, a--, and might store or push either the old or new value depending
    on your language semantics. Currently, we just show an example of incrementing
    the variable in-place, returning no explicit result on the stack.
    """

    def __init__(self, controller):
        """
        :param controller: typically your WasmEmitter or codegen context
          that includes:
            - emit_expression(expr, out_lines): to push the operand's current value
            - _normalize_local_name(name): to reference local variables
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node:
          {
            "type": "PostfixExpression",
            "operator": "++" or "--",
            "operand": { "type": "VariableExpression", "name": "a" },
            "inferred_type": "i32"  # or "i64", "f32", "f64"
          }

        Basic steps:
          1) local.get $a       ; push old value (optional usage)
          2) local.get $a
          3) i32.const 1
          4) i32.add
          5) local.set $a
        """
        op = node["operator"]   # '++' or '--'
        operand = node["operand"]
        operand_type = node.get("inferred_type", "i32")  # default to i32 if missing

        # 1) Load the current variable onto stack (if you need the old value)
        #    e.g. out_lines.append("  local.get $a")
        # For demonstration, we skip pushing it or storing it anywhere,
        # but you could add "local.tee $tempVar" if your language needs oldValue.

        # 2) Re-load the variable to apply the increment/decrement
        self.controller.emit_expression(operand, out_lines)  # e.g. local.get $a

        # 3) Add or subtract 1
        if op == '++':
            if operand_type == "i32":
                out_lines.append("  i32.const 1")
                out_lines.append("  i32.add")
            elif operand_type == "i64":
                out_lines.append("  i64.const 1")
                out_lines.append("  i64.add")
            elif operand_type == "f32":
                out_lines.append("  f32.const 1.0")
                out_lines.append("  f32.add")
            elif operand_type == "f64":
                out_lines.append("  f64.const 1.0")
                out_lines.append("  f64.add")
            else:
                logger.warning(
                    f"Unsupported type '{operand_type}' for postfix '++' operator."
                )
                # You might raise an error or skip codegen
        elif op == '--':
            if operand_type == "i32":
                out_lines.append("  i32.const 1")
                out_lines.append("  i32.sub")
            elif operand_type == "i64":
                out_lines.append("  i64.const 1")
                out_lines.append("  i64.sub")
            elif operand_type == "f32":
                out_lines.append("  f32.const 1.0")
                out_lines.append("  f32.sub")
            elif operand_type == "f64":
                out_lines.append("  f64.const 1.0")
                out_lines.append("  f64.sub")
            else:
                logger.warning(
                    f"Unsupported type '{operand_type}' for postfix '--' operator."
                )
                # Possibly raise an error
        else:
            logger.warning(f"Unknown postfix operator '{op}'; ignoring.")
            return

        # 4) Store the updated value back into the variable
        var_name = operand["name"]
        normalized = self.controller._normalize_local_name(var_name)
        out_lines.append(f"  local.set {normalized}")
