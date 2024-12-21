# compiler/ast/statements/set_statement.py
from compiler.ast.statements.statement import Statement

class SetStatement(Statement):
    """
    Represents 'set <var> <expression>' in LMN.
    Example:
      set x 5
    """
    def __init__(self, variable, expression):
        super().__init__()
        # 'variable' is typically a Variable object or string
        # 'expression' is an Expression node
        self.variable = variable
        self.expression = expression

    def __str__(self):
        return f"set {self.variable} = {self.expression}"

    def to_dict(self):
        return {
            "type": "SetStatement",
            "variable": (
                self.variable.to_dict()
                if hasattr(self.variable, "to_dict")
                else str(self.variable)
            ),
            "expression": (
                self.expression.to_dict()
                if hasattr(self.expression, "to_dict")
                else str(self.expression)
            ),
        }
