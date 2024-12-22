# compiler/parser/function_definition_parser.py

from compiler.lexer.token_type import LmnTokenType
# In the new mega-union approach, you likely re-export FunctionDefinition in compiler.ast.__init__
# So do either:
# from compiler.ast import FunctionDefinition
# or if not re-exported, from compiler.ast.statements.function_definition import FunctionDefinition
from compiler.ast import FunctionDefinition

class FunctionDefinitionParser:
    """
    Parses a function definition statement:
      function <identifier>(param1, param2, ...)
        <statements>
      end
    """
    def __init__(self, parent_parser):
        """
        parent_parser is a reference to the main Parser object,
        which has:
          - current_token
          - advance(), peek(), etc.
          - expression_parser for parsing expressions (if needed)
        """
        self.parser = parent_parser

    def parse(self):
        # We've already seen 'function' in statement_parser,
        # so parse function name, parameters, and body.

        # 1) Expect an identifier for the function name
        func_token = self._expect(LmnTokenType.IDENTIFIER, "Expected function name after 'function'")
        func_name = func_token.value
        self.parser.advance()  # consume function name

        # 2) Expect '('
        self._expect(LmnTokenType.LPAREN, "Expected '(' after function name")
        self.parser.advance()  # consume '('

        # 3) Parse parameter list
        parameters = []
        while self.parser.current_token and self.parser.current_token.token_type != LmnTokenType.RPAREN:
            param_token = self._expect(
                LmnTokenType.IDENTIFIER, 
                "Expected parameter name in function definition"
            )
            parameters.append(param_token.value)
            self.parser.advance()  # consume param name

            # If we see a COMMA, continue parsing more parameters
            if (self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA):
                self.parser.advance()  # consume comma
            else:
                break

        # 4) Expect ')'
        self._expect(LmnTokenType.RPAREN, "Expected ')' after parameter list")
        self.parser.advance()  # consume ')'

        # 5) Parse the function body until 'end'
        body_stmts = self._parse_block(until_tokens=[LmnTokenType.END])

        # 6) Expect 'end'
        self._expect(LmnTokenType.END, "Expected 'end' after function body")
        self.parser.advance()  # consume 'end'

        # Return the constructed FunctionDefinition
        # In the new approach, we do named fields:
        return FunctionDefinition(
            name=func_name,
            parameters=parameters,
            body=body_stmts
        )

    # --------------------------------------
    # Helper Methods
    # --------------------------------------

    def _parse_block(self, until_tokens):
        """
        Parse multiple statements until we hit one of the `until_tokens` or EOF.
        We'll re-use the statement_parser's parse_statement() method.
        """
        statements = []
        while self.parser.current_token and self.parser.current_token.token_type not in until_tokens:
            # skip comments
            if self.parser.current_token.token_type == LmnTokenType.COMMENT:
                self.parser.advance()
                continue

            stmt = self.parser.statement_parser.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                break
        return statements

    def _expect(self, ttype, message):
        """Utility to check current token matches `ttype`."""
        if (not self.parser.current_token 
            or self.parser.current_token.token_type != ttype):
            raise SyntaxError(message)
        return self.parser.current_token
