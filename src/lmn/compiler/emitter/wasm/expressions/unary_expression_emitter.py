# compiler/emitter/wasm/expressions/unary_expression_emitter.py

class UnaryExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is a reference to your main WasmEmitter or
        similar. We'll call controller.emit_expression(...) for
        sub-expressions, and we can also do things like
        controller.local_counter, etc.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node structure (example):
          {
            "type": "UnaryExpression",
            "operator": "-",   # or "+"
            "operand": { ... expression node ... }
          }

        We'll generate code for the operand, then apply the unary op.
        For example:
        - operator "+" => do nothing (just emit the operand)
        - operator "-" => simplest approach is 'i32.const -1' then 'i32.mul'
        - operator "not" => we can do 'i32.eqz' if we interpret 'not' as boolean negation
        """
        op = node["operator"]   # e.g. "-" or "not"
        operand = node["operand"]

        # 1) Emit the operand expression
        self.controller.emit_expression(operand, out_lines)

        # 2) Apply the operator
        if op == "+":
            # unary plus => do nothing; the operand is already on stack
            pass

        elif op == "-":
            # Simpler approach for i32 negation:
            #   (x) => (x * -1)
            out_lines.append('  i32.const -1')
            out_lines.append('  i32.mul')

        elif op == "not":
            # Boolean negation for i32: 0 -> 1, nonzero -> 0
            out_lines.append('  i32.eqz')

        else:
            # fallback / unknown unary operator
            # you might raise an error or do nothing
            pass
