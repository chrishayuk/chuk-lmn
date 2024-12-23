# compiler/parser/statements/for_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.statements.for_statement import ForStatement
from compiler.ast.expressions.variable_expression import VariableExpression

from compiler.parser.parser_utils import expect_token, parse_block

class ForParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        # current_token == FOR, consume it
        self.parser.advance()

        # expect identifier for loop variable
        var_token = expect_token(
            self.parser, 
            LmnTokenType.IDENTIFIER, 
            "Expected loop variable after 'for'"
        )
        # Instead of old 'Variable(...)', do 'VariableExpression(name=...)'
        loop_var = VariableExpression(name=var_token.value)
        self.parser.advance()

        start_expr = None
        end_expr = None
        step_expr = None

        # check for 'in'
        if (self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.IN):
            self.parser.advance()  # consume 'in'
            # for i in expression
            start_expr = self.parser.expression_parser.parse_expression()
        else:
            # for i <start_expr> to <end_expr>
            start_expr = self.parser.expression_parser.parse_expression()
            expect_token(self.parser, LmnTokenType.TO, "Expected 'to' in for-range")
            self.parser.advance()
            end_expr = self.parser.expression_parser.parse_expression()

        # parse the block until 'end'
        body = parse_block(self.parser, [LmnTokenType.END])

        expect_token(self.parser, LmnTokenType.END, "Expected 'end' after for block")
        self.parser.advance()

        # Return a ForStatement with the new field structure
        return ForStatement(
            variable=loop_var,
            start_expr=start_expr,
            end_expr=end_expr,
            step_expr=step_expr,
            body=body
        )
