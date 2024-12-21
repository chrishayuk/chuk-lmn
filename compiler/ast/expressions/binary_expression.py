# compiler/ast/expressions/binary_expression.py
from compiler.ast.expressions.expression import Expression

class BinaryExpression(Expression):
    def __init__(self, left, operator, right):
        super().__init__()
        self.left = left     # Expression
        self.operator = operator  # Something like LmnTokenType or an operator string
        self.right = right   # Expression

    def __str__(self):
        # Use the operator's value directly if it exists, else str(operator)
        op_str = getattr(self.operator, 'value', str(self.operator))
        return f"({self.left} {op_str} {self.right})"

    def to_dict(self):
        # Recursively build a dict structure
        op_str = getattr(self.operator, 'value', str(self.operator))
        return {
            "type": "BinaryExpression",
            "operator": op_str,
            "left": self.left.to_dict() if hasattr(self.left, 'to_dict') else str(self.left),
            "right": self.right.to_dict() if hasattr(self.right, 'to_dict') else str(self.right),
        }
