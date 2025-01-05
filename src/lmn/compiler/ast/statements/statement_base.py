# lmn/compiler/ast/statements/statement.py
from __future__ import annotations
from lmn.compiler.ast.ast_node import ASTNode

class StatementBase(ASTNode):
    """
    Base class for all LMN statement AST nodes.
    """
    def __repr__(self):
        # output the node as a string
        fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())

        # return the string representation of the object
        return f"{self.__class__.__name__}({fields_str})"