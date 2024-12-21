# compiler/ast/expressions/literal.py
import decimal
from compiler.ast.expressions.expression import Expression

class Literal(Expression):
    def __init__(self, value):
        # call parent
        super().__init__()
    
        try:
            # Attempt to parse numeric
            self.value = decimal.Decimal(value)
        except (ValueError, decimal.InvalidOperation):
            # Not numeric, keep as string or other type
            self.value = value

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        # If it's a Decimal, convert to int or float when possible
        if isinstance(self.value, decimal.Decimal):
            if self.value % 1 == 0:
                return {
                    "type": "LiteralExpression",
                    "value": int(self.value)
                }
            else:
                return {
                    "type": "LiteralExpression",
                    "value": float(self.value)
                }
        else:
            # Non-numeric or string
            return {
                "type": "LiteralExpression",
                "value": self.value
            }
