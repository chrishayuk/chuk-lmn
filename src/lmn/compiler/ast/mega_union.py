# file: lmn/compiler/ast/mega_union.py
from typing import Annotated, Union
from pydantic import Field

#
# 1) Import all expression submodels
#    (If any submodel references 'Node', we'll skip rebuilding until after Node is declared.)
#
from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression

# set the expression union type
Expression = Annotated[
    Union[
        LiteralExpression,
        VariableExpression,
        BinaryExpression,
        UnaryExpression,
        FnExpression,
        ConversionExpression,
        PostfixExpression,
        AssignmentExpression,
        JsonLiteralExpression,
        ArrayLiteralExpression,
        AnonymousFunctionExpression
    ],
    Field(discriminator="type")
]

# Rebuild expression submodels that do NOT reference 'Node'
LiteralExpression.model_rebuild()
VariableExpression.model_rebuild()
BinaryExpression.model_rebuild()
UnaryExpression.model_rebuild()
PostfixExpression.model_rebuild()
FnExpression.model_rebuild()
AnonymousFunctionExpression.model_rebuild()
AssignmentExpression.model_rebuild()
ConversionExpression.model_rebuild()
JsonLiteralExpression.model_rebuild()
ArrayLiteralExpression.model_rebuild()

#
# 2) Import statement submodels
#

from lmn.compiler.ast.statements.block_statement import BlockStatement
from lmn.compiler.ast.statements.function_parameter import FunctionParameter
from lmn.compiler.ast.statements.if_statement import IfStatement
from lmn.compiler.ast.statements.else_if_clause import ElseIfClause
from lmn.compiler.ast.statements.for_statement import ForStatement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition
from lmn.compiler.ast.statements.print_statement import PrintStatement
from lmn.compiler.ast.statements.return_statement import ReturnStatement
from lmn.compiler.ast.statements.assignment_statement import AssignmentStatement
from lmn.compiler.ast.statements.let_statement import LetStatement
from lmn.compiler.ast.statements.call_statement import CallStatement

Statement = Annotated[
    Union[
        # If you want them all in one union, list them here
        IfStatement,
        ElseIfClause,
        ForStatement,
        AssignmentStatement,
        LetStatement,
        FunctionParameter,
        FunctionDefinition,
        ReturnStatement,
        PrintStatement,
        CallStatement,
        BlockStatement,
    ],
    Field(discriminator="type")
]

#
# 3) Import Program (which references 'Node' in body: List['Node'])
#
from lmn.compiler.ast.program import Program
Node = Annotated[
    Union[
        Expression,   # union of all expression submodels
        Statement,    # union of all statement submodels
        Program       # Program references 'Node'
    ],
    Field(discriminator="type")
]

# rebuild models
IfStatement.model_rebuild(force=True)
ElseIfClause.model_rebuild(force=True)
CallStatement.model_rebuild(force=True)
AssignmentStatement.model_rebuild(force=True)
PrintStatement.model_rebuild(force=True)
FunctionParameter.model_rebuild(force=True)
FunctionDefinition.model_rebuild(force=True)
ReturnStatement.model_rebuild(force=True)
LetStatement.model_rebuild(force=True)
ForStatement.model_rebuild(force=True)
BlockStatement.model_rebuild(force=True)

ReturnStatement.model_rebuild(force=True)
BinaryExpression.model_rebuild(force=True)
AnonymousFunctionExpression.model_rebuild(force=True)

# rebuild program node
Program.model_rebuild()