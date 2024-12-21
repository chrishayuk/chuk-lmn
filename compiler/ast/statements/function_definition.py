# compiler/ast/statements/function_definition.py
from compiler.ast.statements.statement import Statement

class FunctionDefinition(Statement):
    """
    Represents a top-level 'function' definition in LMN:
      function foo(a, b)
        ...
      end
    """
    def __init__(self, name, parameters, body):
        super().__init__()
        self.name = name               # e.g. "factorial"
        self.parameters = parameters   # list of strings or Variables
        self.body = body               # list of statements

    def __str__(self):
        params_str = ", ".join(self.parameters)
        body_str = " ".join(str(stmt) for stmt in self.body)
        return f"function {self.name}({params_str}) [body: {body_str}]"

    def to_dict(self):
        return {
            "type": "FunctionDefinition",
            "name": self.name,
            "params": self.parameters,
            "body": [
                stmt.to_dict() if hasattr(stmt, "to_dict") else str(stmt)
                for stmt in self.body
            ],
        }
