# compiler/ast/expressions/unary_expression.py
from compiler.ast.expressions.expression import Expression

class UnaryExpression(Expression):
    def __init__(self, operator, operand):
        super().__init__()
        self.operator = operator  # e.g. LmnTokenType.NOT
        self.operand = operand    # Expression

    def __str__(self):
        op_str = getattr(self.operator, 'value', str(self.operator))
        return f"({op_str} {self.operand})"

    def to_dict(self):
        op_str = getattr(self.operator, 'value', str(self.operator))
        return {
            "type": "UnaryExpression",
            "operator": op_str,
            "operand": (
                self.operand.to_dict()
                if hasattr(self.operand, 'to_dict')
                else str(self.operand)
            ),
        }
