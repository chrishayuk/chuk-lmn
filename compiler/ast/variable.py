# compiler/ast/variable.py
from compiler.ast.ast_node import ASTNode

class Variable(ASTNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "type": "Variable",
            "name": self.name
        }
