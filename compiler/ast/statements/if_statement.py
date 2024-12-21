# compiler/ast/statements/if_statement.py
from compiler.ast.statements.statement import Statement

class IfStatement(Statement):
    """
    Represents an 'if (condition)' statement with optional 'else' body.
    Syntax in LMN might be:
    
      if (condition)
        <then statements>
      else
        <else statements>
      end
    """
    def __init__(self, condition, then_body, else_body=None):
        super().__init__()
        # 'condition' is an Expression
        self.condition = condition
        
        # 'then_body' can be a list of statements or a single statement
        # In many parsers, you store them as a list.
        self.then_body = then_body if isinstance(then_body, list) else [then_body]

        # 'else_body' is optional
        if else_body is None:
            self.else_body = []
        elif isinstance(else_body, list):
            self.else_body = else_body
        else:
            self.else_body = [else_body]

    def __str__(self):
        # string representation for debugging
        cond_str = str(self.condition)
        then_str = " ".join(str(st) for st in self.then_body)
        else_str = " ".join(str(st) for st in self.else_body)
        if else_str:
            return f"if {cond_str} [then: {then_str}] [else: {else_str}]"
        else:
            return f"if {cond_str} [then: {then_str}]"

    def to_dict(self):
        return {
            "type": "IfStatement",
            "condition": (
                self.condition.to_dict()
                if hasattr(self.condition, "to_dict")
                else str(self.condition)
            ),
            "thenBody": [
                stmt.to_dict() if hasattr(stmt, "to_dict") else str(stmt)
                for stmt in self.then_body
            ],
            "elseBody": [
                stmt.to_dict() if hasattr(stmt, "to_dict") else str(stmt)
                for stmt in self.else_body
            ],
        }
