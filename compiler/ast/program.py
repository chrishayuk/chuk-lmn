# compiler/ast/program.py
import json
from compiler.ast.ast_node import ASTNode

class Program(ASTNode):
    """
    LMN Program node that contains a list of top-level statements
    (which might include function definitions).
    """
    def __init__(self, body=None):
        # call the parent constructor
        super().__init__()

        # We'll store all top-level statements in a list
        self.body = body if body else []

    def add_statement(self, stmt):
        self.body.append(stmt)

    def to_dict(self):
        return {
            "type": "Program",
            "body": [
                stmt.to_dict() if hasattr(stmt, "to_dict") else str(stmt)
                for stmt in self.body
            ]
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)
