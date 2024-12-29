# file: lmn/compiler/parser/statements/assignment_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token
from lmn.compiler.ast.statements.assignment_statement import AssignmentStatement
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression

class AssignmentParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parse an assignment statement of form:
            myVar = expression
            myVar += expression
            myVar -= expression
            etc.
        """
        # 1) Expect an IDENTIFIER for the variable name
        var_token = expect_token(
            self.parser,
            LmnTokenType.IDENTIFIER,
            "Expected variable name for assignment"
        )
        var_name = var_token.value
        self.parser.advance()  # consume the identifier

        # 2) Check if the next token is =, +=, -=, etc.
        op_token = self.parser.current_token
        if not op_token:
            raise SyntaxError("Expected assignment operator after variable name")

        # We can allow more, e.g. LmnTokenType.MUL_EQ, DIV_EQ, etc. if your language supports them
        valid_ops = (
            LmnTokenType.EQ,       # =
            LmnTokenType.PLUS_EQ,  # +=
            LmnTokenType.MINUS_EQ, # -=
        )
        if op_token.token_type not in valid_ops:
            raise SyntaxError(f"Unexpected assignment operator: {op_token.value}")

        self.parser.advance()  # consume the assignment operator

        # 3) Parse right-hand side expression
        rhs_expr = self.parser.expression_parser.parse_expression()
        if rhs_expr is None:
            raise SyntaxError("Expected expression after assignment operator")

        # 4) Build and return the AssignmentStatement node
        #    If it's just '=', direct assignment
        if op_token.token_type == LmnTokenType.EQ:
            return AssignmentStatement(
                variable_name=var_name,
                expression=rhs_expr
            )

        #    If it's '+=', build a small binary expr for (var + RHS)
        elif op_token.token_type == LmnTokenType.PLUS_EQ:
            plus_expr = BinaryExpression(
                operator='+',
                left=VariableExpression(name=var_name),
                right=rhs_expr
            )
            return AssignmentStatement(
                variable_name=var_name,
                expression=plus_expr
            )

        #    If it's '-=', build a small binary expr for (var - RHS)
        elif op_token.token_type == LmnTokenType.MINUS_EQ:
            minus_expr = BinaryExpression(
                operator='-',
                left=VariableExpression(name=var_name),
                right=rhs_expr
            )
            return AssignmentStatement(
                variable_name=var_name,
                expression=minus_expr
            )

        # If you support more compound ops, handle them similarly
        raise SyntaxError(f"Unhandled assignment operator: {op_token.value}")
