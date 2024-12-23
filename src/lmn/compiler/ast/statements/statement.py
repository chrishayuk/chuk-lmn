# lmn/compiler/ast/statements/statement.py
from __future__ import annotations
from lmn.compiler.ast.ast_node import ASTNode

class Statement(ASTNode):
    """
    Base class for all LMN statement AST nodes.
    """
    def __repr__(self):
        fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields_str})"
