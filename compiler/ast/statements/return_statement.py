# compiler/ast/statements/return_statement.py
from compiler.ast.statements.statement import Statement

class ReturnStatement(Statement):
    """
    Represents 'return <expression>' in LMN.
    Example:
      return n * fact(n - 1)
    """
    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def __str__(self):
        return f"return {self.expression}"

    def to_dict(self):
        return {
            "type": "ReturnStatement",
            "expression": (
                self.expression.to_dict()
                if hasattr(self.expression, "to_dict")
                else str(self.expression)
            ),
        }
