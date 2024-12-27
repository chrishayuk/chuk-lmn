# function_definition_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import FunctionDefinition

class FunctionDefinitionParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        # 'function' is already consumed in statement_parser.
        func_token = self._expect(LmnTokenType.IDENTIFIER, "Expected function name after 'function'")
        func_name = func_token.value
        self.parser.advance()  # consume function name

        self._expect(LmnTokenType.LPAREN, "Expected '(' after function name")
        self.parser.advance()  # consume '('

        # parse zero or more params
        params = []
        while (self.parser.current_token 
               and self.parser.current_token.token_type != LmnTokenType.RPAREN):
            param_token = self._expect(LmnTokenType.IDENTIFIER, "Expected param name")
            params.append(param_token.value)
            self.parser.advance()  # consume param

            if (self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.COMMA):
                self.parser.advance()  # consume comma
            else:
                break

        self._expect(LmnTokenType.RPAREN, "Expected ')' after parameters")
        self.parser.advance()  # consume ')'

        # parse function body until 'end'
        body_stmts = self._parse_block(until_tokens=[LmnTokenType.END])

        self._expect(LmnTokenType.END, "Expected 'end' after function body")
        self.parser.advance()  # consume 'end'

        return FunctionDefinition(
            name=func_name,
            params=params,
            body=body_stmts
        )

    def _parse_block(self, until_tokens):
        """
        Reads statements until one of `until_tokens` is found.
        Also skip COMMENT/NEWLINE tokens here, if needed.
        """
        statements = []
        while (self.parser.current_token 
               and self.parser.current_token.token_type not in until_tokens):

            # skip COMMENT, NEWLINE if you want to allow blank lines in the body
            if self.parser.current_token.token_type in (LmnTokenType.COMMENT, LmnTokenType.NEWLINE):
                self.parser.advance()
                continue

            stmt = self.parser.statement_parser.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # If parse_statement returned None, we can break or consume a token
                self.parser.advance()
        return statements

    def _expect(self, ttype, msg):
        """
        Checks that current_token is `ttype`.
        Does NOT advance; do that yourself.
        """
        if (not self.parser.current_token 
            or self.parser.current_token.token_type != ttype):
            raise SyntaxError(msg)
        return self.parser.current_token
