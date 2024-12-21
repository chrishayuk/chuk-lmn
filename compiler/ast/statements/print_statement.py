# compiler/ast/statements/print_statement.py
from compiler.ast.statements.statement import Statement

class PrintStatement(Statement):
    """
    Represents 'print <expr1> <expr2> ...'
    Example:
      print "Hello" x
    """
    def __init__(self, expressions):
        super().__init__()
        # expressions is a list of Expression nodes
        self.expressions = expressions

    def __str__(self):
        expr_str = " ".join(str(expr) for expr in self.expressions)
        return f"print {expr_str}"

    def to_dict(self):
        return {
            "type": "PrintStatement",
            "expressions": [
                expr.to_dict() if hasattr(expr, 'to_dict') else str(expr)
                for expr in self.expressions
            ],
        }
