# set_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token, current_token_is
from lmn.compiler.ast import SetStatement, VariableExpression

class SetParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parses statements like:
          set x = 5
          set int.32 x = 5
          set y
        """
        # 1) consume the 'set' token
        self.parser.advance()  

        # 2) optional type annotation
        type_annotation = None
        if self._lookahead_is_type_annotation():
            type_annotation = self._parse_type_annotation()

        # 3) expect IDENTIFIER for variable name
        var_token = expect_token(self.parser, LmnTokenType.IDENTIFIER,
                                 "Expected variable name after 'set'")
        # CRITICAL: consume that IDENTIFIER token 
        self.parser.advance()

        # 4) optional '=' <expr>
        initializer_expr = None
        if current_token_is(self.parser, LmnTokenType.EQ):
            self.parser.advance()  # consume '='
            initializer_expr = self.parser.expression_parser.parse_expression()

        return SetStatement(
            variable=VariableExpression(name=var_token.value),
            expression=initializer_expr,
            type_annotation=type_annotation
        )


    def _lookahead_is_type_annotation(self):
        """Check if next tokens look like IDENTIFIER '.' NUMBER."""
        t1 = self.parser.peek(0)  # current token
        t2 = self.parser.peek(1)  # next
        t3 = self.parser.peek(2)
        return (
            t1 and t1.token_type == LmnTokenType.IDENTIFIER and
            t2 and t2.token_type == LmnTokenType.DOT and
            t3 and t3.token_type == LmnTokenType.NUMBER
        )

    def _parse_type_annotation(self):
        """Consumes IDENTIFIER, DOT, NUMBER => e.g. 'float.32'."""
        if self.parser.current_token.token_type != LmnTokenType.IDENTIFIER:
            raise SyntaxError("Expected type name (e.g. 'float')")
        part1_token = self.parser.current_token
        self.parser.advance()

        if self.parser.current_token.token_type != LmnTokenType.DOT:
             raise SyntaxError("Expected '.' in type annotation")
        self.parser.advance()

        if self.parser.current_token.token_type != LmnTokenType.NUMBER:
             raise SyntaxError("Expected bit-size after '.' (e.g. 32)")

        bits_token = self.parser.current_token
        self.parser.advance()

        return f"{part1_token.value}.{int(bits_token.value)}"
