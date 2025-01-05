# lmn/compiler/ast/node_kind.pys
from enum import Enum

class NodeKind(str, Enum):
    # Expressions
    LITERAL = "LiteralExpression"
    VARIABLE = "VariableExpression"
    BINARY = "BinaryExpression"
    UNARY = "UnaryExpression"
    FN = "FnExpression"
    POSTFIX = "PostfixExpression"
    ASSIGNMENTEXPRESSION = "AssignmentExpression"
    ARRAY_LITERAL = "ArrayLiteralExpression"
    JSON_LITERAL = "JsonLiteralExpression"
    CONVERSION_EXPRESSION = "ConversionExpression"
    ANONYMOUS_FUNCTION = "AnonymousFunction"

    # Statements
    CALL = "CallStatement"
    FOR = "ForStatement"
    FUNCTION_DEF = "FunctionDefinition"
    FUNCTION_PARAMETER = "FunctionParameter"
    IF = "IfStatement"
    ELSEIF = "ElseIfClause"
    PRINT = "PrintStatement"
    RETURN = "ReturnStatement"
    LET = "LetStatement"
    ASSIGNMENTSTATEMENT = "AssignmentStatement"
    BLOCK = "BlockStatement"
