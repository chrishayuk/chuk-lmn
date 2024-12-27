# lmn/compiler/ast/node_kind.pys
from enum import Enum

class NodeKind(str, Enum):
    # Expressions
    LITERAL = "LiteralExpression"
    VARIABLE = "VariableExpression"
    BINARY = "BinaryExpression"
    UNARY = "UnaryExpression"
    FN = "FnExpression"

    # Statements
    CALL = "CallStatement"
    FOR = "ForStatement"
    FUNCTION_DEF = "FunctionDefinition"
    IF = "IfStatement"
    PRINT = "PrintStatement"
    RETURN = "ReturnStatement"
    LET = "LetStatement"
    ASSIGNMENT = "AssignmentStatement"
