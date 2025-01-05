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

# Program
from lmn.compiler.ast.program import Program

#
# Rebuild calls
#

# Expressions
LiteralExpression.model_rebuild()
VariableExpression.model_rebuild()
BinaryExpression.model_rebuild()
UnaryExpression.model_rebuild()
FnExpression.model_rebuild()
AssignmentExpression.model_rebuild()
PostfixExpression.model_rebuild()
JsonLiteralExpression.model_rebuild()
ArrayLiteralExpression.model_rebuild()
AnonymousFunctionExpression.model_rebuild()

# Statements
CallStatement.model_rebuild()
ForStatement.model_rebuild()
FunctionDefinition.model_rebuild()
FunctionParameter.model_rebuild()
ReturnStatement.model_rebuild()
IfStatement.model_rebuild()
PrintStatement.model_rebuild()
AssignmentStatement.model_rebuild()
LetStatement.model_rebuild()

ReturnStatement.model_rebuild(force=True)
BinaryExpression.model_rebuild(force=True)

# Program
Program.model_rebuild()
