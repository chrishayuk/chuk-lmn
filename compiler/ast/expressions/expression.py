# compiler/ast/expressions/expression.py
from compiler.ast.ast_node import ASTNode

class Expression(ASTNode):
    """
    Base class for all expression nodes in the LMN AST.
    """
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({', '.join([f'{k}={repr(v)}' for k, v in self.__dict__.items()])})"
        )
