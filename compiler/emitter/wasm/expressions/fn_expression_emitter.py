# compiler/emitter/wasm/expressions/fn_expression_emitter.py
class FnExpressionEmitter:
    def __init__(self, controller):
        # set the controller
        self.controller = controller

    def emit_fn(self, node, out_lines):
        """
        node: { "type": "FnExpression",
                "name": { "type": "Variable", "name": "factorial" },
                "arguments": [ expr1, expr2, ... ]
              }
        """
        func_name = node["name"]["name"]

        # evaluate arguments
        for arg in node["arguments"]:
            self.controller.emit_expression(arg, out_lines)
        
        # append
        out_lines.append(f'  call ${func_name}')
