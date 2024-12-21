# compiler/ast/expressions/fn_expression.py
from typing import List
from compiler.ast.expressions.expression import Expression

class FnExpression(Expression):
    """
    Represents a function call or invocation in LMN: e.g. fact(x - 1).
    """
    def __init__(self, name, arguments: List[Expression]):
        super().__init__()
        self.name = name          # Often a Variable
        self.arguments = arguments

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"

    def to_dict(self):
        return {
            "type": "FnExpression",
            "name": (
                self.name.to_dict() if hasattr(self.name, 'to_dict') else str(self.name)
            ),
            "arguments": [
                arg.to_dict() if hasattr(arg, 'to_dict') else str(arg)
                for arg in self.arguments
            ],
        }
