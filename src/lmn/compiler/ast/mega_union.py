# file: lmn/compiler/ast/mega_union.py
from typing import Annotated, Union
from pydantic import Field

print("[DEBUG] Loading mega_union.py...")

#
# 1) Import all expression submodels
#    (If any submodel references 'Node', we'll skip rebuilding until after Node is declared.)
#

print("[DEBUG] Importing expression submodels...")

from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression

print("[DEBUG] Defining Expression union...")

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

print("[DEBUG] Expression union declared. Rebuilding expression submodels...")

# Rebuild expression submodels that do NOT reference 'Node'
LiteralExpression.model_rebuild()
VariableExpression.model_rebuild()
BinaryExpression.model_rebuild()
UnaryExpression.model_rebuild()
FnExpression.model_rebuild()

print("[DEBUG] Rebuilt expression submodels.")

#
# 2) Import statement submodels
#

print("[DEBUG] Importing statement submodels...")

from lmn.compiler.ast.statements.if_statement import IfStatement
from lmn.compiler.ast.statements.for_statement import ForStatement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition
from lmn.compiler.ast.statements.print_statement import PrintStatement
from lmn.compiler.ast.statements.return_statement import ReturnStatement
from lmn.compiler.ast.statements.set_statement import SetStatement
from lmn.compiler.ast.statements.call_statement import CallStatement

print("[DEBUG] Defining Statement union...")

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

print("[DEBUG] Statement union declared.")

#
# 3) Import Program (which references 'Node' in body: List['Node'])
#

print("[DEBUG] Importing Program, which references 'Node'...")
from lmn.compiler.ast.program import Program
print("[DEBUG] Defining Node union now...")
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

print("[DEBUG] Now calling Program.model_rebuild() to finalize references to 'Node'.")
Program.model_rebuild()
print("[DEBUG] Program.model_rebuild() done.")