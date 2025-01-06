# file: lmn/compiler/ast/__init__.py
from __future__ import annotations

from lmn.compiler.ast.statements.function_parameter import FunctionParameter

# Common
from .ast_node import ASTNode
from .node_kind import NodeKind

# Mega Union (where Expression, Statement, Node are defined)
# We'll re-export them from here for convenience.
from .mega_union import Expression, Statement, Node

# Expressions - submodels
from .expressions.expression_base import ExpressionBase
from .expressions.literal_expression import LiteralExpression
from .expressions.variable_expression import VariableExpression
from .expressions.binary_expression import BinaryExpression
from .expressions.unary_expression import UnaryExpression
from .expressions.fn_expression import FnExpression
from .expressions.postfix_expression import PostfixExpression
from .expressions.array_literal_expression import ArrayLiteralExpression
from .expressions.assignment_expression import AssignmentExpression
from .expressions.json_literal_expression import JsonLiteralExpression
from .expressions.anonymous_function_expression import AnonymousFunctionExpression

# Statements - submodels
from .statements.call_statement import CallStatement
from .statements.for_statement import ForStatement
from .statements.function_definition import FunctionDefinition
from .statements.if_statement import IfStatement
from .statements.print_statement import PrintStatement
from .statements.return_statement import ReturnStatement
from .statements.let_statement import LetStatement
from .statements.assignment_statement import AssignmentStatement
from .statements.block_statement import BlockStatement

# Program
from lmn.compiler.ast.program import Program

#
# Rebuild calls — now in a single block, each with force=True
# so Pydantic can finalize forward references
#

# Expressions
LiteralExpression.model_rebuild(force=True)
VariableExpression.model_rebuild(force=True)
BinaryExpression.model_rebuild(force=True)
UnaryExpression.model_rebuild(force=True)
FnExpression.model_rebuild(force=True)
AssignmentExpression.model_rebuild(force=True)
PostfixExpression.model_rebuild(force=True)
JsonLiteralExpression.model_rebuild(force=True)
ArrayLiteralExpression.model_rebuild(force=True)
AnonymousFunctionExpression.model_rebuild(force=True)

# Statements
CallStatement.model_rebuild(force=True)
ForStatement.model_rebuild(force=True)
FunctionDefinition.model_rebuild(force=True)
FunctionParameter.model_rebuild(force=True)
ReturnStatement.model_rebuild(force=True)
IfStatement.model_rebuild(force=True)
PrintStatement.model_rebuild(force=True)
AssignmentStatement.model_rebuild(force=True)
LetStatement.model_rebuild(force=True)
BlockStatement.model_rebuild(force=True)

# Program
Program.model_rebuild(force=True)
