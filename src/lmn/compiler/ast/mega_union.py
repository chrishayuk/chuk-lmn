# file: lmn/compiler/ast/mega_union.py
from typing import Annotated, Union
from pydantic import Field

#
# 1) Import all expression submodels
#    (If any submodel references 'Node', we'll skip rebuilding until after Node is declared.)
#
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression

# set the expression union type
Expression = Annotated[
    Union[
        LiteralExpression,
        VariableExpression,
        BinaryExpression,
        UnaryExpression,
        FnExpression,
    ],
    Field(discriminator="type")
]

# Rebuild expression submodels that do NOT reference 'Node'
LiteralExpression.model_rebuild()
VariableExpression.model_rebuild()
BinaryExpression.model_rebuild()
UnaryExpression.model_rebuild()
FnExpression.model_rebuild()

#
# 2) Import statement submodels
#

from lmn.compiler.ast.statements.if_statement import IfStatement
from lmn.compiler.ast.statements.for_statement import ForStatement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition
from lmn.compiler.ast.statements.print_statement import PrintStatement
from lmn.compiler.ast.statements.return_statement import ReturnStatement
from lmn.compiler.ast.statements.set_statement import SetStatement
from lmn.compiler.ast.statements.call_statement import CallStatement

Statement = Annotated[
    Union[
        # If you want them all in one union, list them here
        IfStatement,
        ForStatement,
        SetStatement,
        ReturnStatement,
        FunctionDefinition,
        PrintStatement,
        CallStatement,  # Add any statement submodels
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
IfStatement.model_rebuild()
CallStatement.model_rebuild()
SetStatement.model_rebuild()
ReturnStatement.model_rebuild()
PrintStatement.model_rebuild()
FunctionDefinition.model_rebuild()
ForStatement.model_rebuild()

# rebuild program node
Program.model_rebuild()