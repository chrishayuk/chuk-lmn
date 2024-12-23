# compiler/ast/__init__.py
from __future__ import annotations

# Common
from .ast_node import ASTNode
from .node_kind import NodeKind
from .mega_union import MegaUnion

# Expressions
from .expressions.literal_expression import LiteralExpression
from .expressions.variable_expression import VariableExpression
from .expressions.binary_expression import BinaryExpression
from .expressions.unary_expression import UnaryExpression
from .expressions.fn_expression import FnExpression

# Statements
from .statements.call_statement import CallStatement
from .statements.for_statement import ForStatement
from .statements.function_definition import FunctionDefinition
from .statements.if_statement import IfStatement
from .statements.print_statement import PrintStatement
from .statements.return_statement import ReturnStatement
from .statements.set_statement import SetStatement

# Program
from compiler.ast.program import Program

# Rebuild them all
LiteralExpression.model_rebuild()
VariableExpression.model_rebuild()
BinaryExpression.model_rebuild()
UnaryExpression.model_rebuild()
FnExpression.model_rebuild()

CallStatement.model_rebuild()
ForStatement.model_rebuild()
FunctionDefinition.model_rebuild()
IfStatement.model_rebuild()
PrintStatement.model_rebuild()
ReturnStatement.model_rebuild()
SetStatement.model_rebuild()

Program.model_rebuild()
