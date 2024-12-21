# compiler/ast/expressions/expression.py
from typing import Literal
from compiler.ast.ast_node import ASTNode
from compiler.ast.expressions.expression_kind import ExpressionKind

class Expression(ASTNode):
    """
    Base class for all expression nodes in the LMN AST.
    We store a 'type' field indicating which expression subclass we are.
    """
    type: Literal[ExpressionKind.EXPRESSION] = ExpressionKind.EXPRESSION

    
