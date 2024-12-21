# compiler/ast/statements/call_statement.py
from compiler.ast.statements.statement import Statement

class CallStatement(Statement):
    """
    Represents:
      call "someTool" expr1 expr2 ...
    """
    def __init__(self, tool_name, arguments):
        super().__init__()
        self.tool_name = tool_name  # string or maybe a Literal
        self.arguments = arguments  # list of Expression

    def __str__(self):
        args_str = " ".join(str(arg) for arg in self.arguments)
        return f'call "{self.tool_name}" {args_str}'

    def to_dict(self):
        return {
            "type": "CallStatement",
            "toolName": self.tool_name if isinstance(self.tool_name, str) else str(self.tool_name),
            "arguments": [
                arg.to_dict() if hasattr(arg, "to_dict") else str(arg)
                for arg in self.arguments
            ],
        }
