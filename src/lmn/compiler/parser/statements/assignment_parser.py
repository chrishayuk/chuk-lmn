# lmn/compiler/parser/statements/assignment_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token
from lmn.compiler.ast.statements.assignment_statement import AssignmentStatement

class AssignmentParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parse an assignment statement of form:
            myVar = expression
        """
        # 1) Expect an IDENTIFIER for the variable name
        var_token = expect_token(
            self.parser, 
            LmnTokenType.IDENTIFIER,
            "Expected variable name for assignment"
        )
        self.parser.advance()

        # 2) Expect '='
        eq_token = expect_token(
            self.parser, 
            LmnTokenType.EQ,
            "Expected '=' for assignment statement"
        )
        self.parser.advance()

        # 3) Parse expression
        rhs_expr = self.parser.expression_parser.parse_expression()

        # 4) Build and return the AssignmentStatement node
        return AssignmentStatement(
            variable_name=var_token.value,
            expression=rhs_expr
        )
