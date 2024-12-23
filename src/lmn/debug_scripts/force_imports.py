# force_imports.py
print("=== Forcibly importing expression classes in a known order ===")
import lmn.compiler.ast.expressions.literal_expression
import lmn.compiler.ast.expressions.variable_expression
import lmn.compiler.ast.expressions.binary_expression
import lmn.compiler.ast.expressions.unary_expression
import lmn.compiler.ast.expressions.fn_expression

print("=== Forcibly importing them from the package to call model_rebuild ===")
from lmn.compiler.ast import (
    LiteralExpression,
    VariableExpression,
    BinaryExpression,
    UnaryExpression,
    FnExpression
)
LiteralExpression.model_rebuild()
VariableExpression.model_rebuild()
BinaryExpression.model_rebuild()
UnaryExpression.model_rebuild()
FnExpression.model_rebuild()

print("=== Now forcibly importing statement classes in a known order ===")
import lmn.compiler.ast.statements.call_statement
import lmn.compiler.ast.statements.for_statement
import lmn.compiler.ast.statements.function_definition
import lmn.compiler.ast.statements.if_statement
import lmn.compiler.ast.statements.print_statement
import lmn.compiler.ast.statements.return_statement
import lmn.compiler.ast.statements.set_statement

print("=== Forcibly importing them from the package to call model_rebuild ===")
from lmn.compiler.ast import (
    CallStatement,
    ForStatement,
    FunctionDefinition,
    IfStatement,
    PrintStatement,
    ReturnStatement,
    SetStatement
)
CallStatement.model_rebuild()
ForStatement.model_rebuild()
FunctionDefinition.model_rebuild()
IfStatement.model_rebuild()
PrintStatement.model_rebuild()
ReturnStatement.model_rebuild()
SetStatement.model_rebuild()

print("=== Now everything should be fully defined. Running debug_fields.py. ===")
import lmn.debug_scripts.debug_fields as debug_fields
