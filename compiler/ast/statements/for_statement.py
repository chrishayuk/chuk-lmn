# compiler/ast/statements/for_statement.py
from compiler.ast.statements.statement import Statement

class ForStatement(Statement):
    """
    Represents either:
      for i 1 to 5
        <statements>
      end
    or
      for item in items
        <statements>
      end
    depending on DSL design.
    """
    def __init__(self, variable, start_expr, end_expr, step_expr=None, body=None):
        super().__init__()
        # For numeric range: e.g. for i 1 to 5
        self.variable = variable   # usually a Variable node
        self.start_expr = start_expr  # Expression or None
        self.end_expr = end_expr      # Expression or None
        self.step_expr = step_expr    # Expression or None
        self.body = body if body else []  # List of statements

    def __str__(self):
        # If step_expr is present, show it, otherwise omit
        step_part = f" step {self.step_expr}" if self.step_expr else ""
        body_str = " ".join(str(stmt) for stmt in self.body)
        return f"for {self.variable} {self.start_expr} to {self.end_expr}{step_part} [body: {body_str}]"

    def to_dict(self):
        return {
            "type": "ForStatement",
            "variable": (
                self.variable.to_dict()
                if hasattr(self.variable, "to_dict")
                else str(self.variable)
            ),
            "start": (
                self.start_expr.to_dict()
                if (self.start_expr and hasattr(self.start_expr, "to_dict"))
                else str(self.start_expr)
                if self.start_expr
                else None
            ),
            "end": (
                self.end_expr.to_dict()
                if (self.end_expr and hasattr(self.end_expr, "to_dict"))
                else str(self.end_expr)
                if self.end_expr
                else None
            ),
            "step": (
                self.step_expr.to_dict()
                if (self.step_expr and hasattr(self.step_expr, "to_dict"))
                else str(self.step_expr)
                if self.step_expr
                else None
            ),
            "body": [
                stmt.to_dict() if hasattr(stmt, "to_dict") else str(stmt)
                for stmt in self.body
            ],
        }
