# force_imports.py
print("=== Forcibly importing expression classes in a known order ===")
import compiler.ast.expressions.literal_expression
import compiler.ast.expressions.variable_expression
import compiler.ast.expressions.binary_expression
import compiler.ast.expressions.unary_expression
import compiler.ast.expressions.fn_expression

print("=== Forcibly importing them from the package to call model_rebuild ===")
from compiler.ast import (
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
import compiler.ast.statements.call_statement
import compiler.ast.statements.for_statement
import compiler.ast.statements.function_definition
import compiler.ast.statements.if_statement
import compiler.ast.statements.print_statement
import compiler.ast.statements.return_statement
import compiler.ast.statements.set_statement

print("=== Forcibly importing them from the package to call model_rebuild ===")
from compiler.ast import (
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
import debug_fields
