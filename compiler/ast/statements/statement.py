# compiler/ast/statements/statement.py
from compiler.ast.ast_node import ASTNode

class Statement(ASTNode):
    """
    Base class for all LMN statement AST nodes.
    """
    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
            + ")"
        )
