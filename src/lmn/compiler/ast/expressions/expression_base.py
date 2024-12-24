# file: lmn/compiler/ast/expressions/expression_base.py
from typing import Optional

# import ast's
from lmn.compiler.ast.ast_node import ASTNode

class ExpressionBase(ASTNode):
    """
    A base for all expressions. Inherits from ASTNode (which is a Pydantic BaseModel).
    We can store 'inferred_type' or other common expression fields here.
    """
    inferred_type: Optional[str] = None
