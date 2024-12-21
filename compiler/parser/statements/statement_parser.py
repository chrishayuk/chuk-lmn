# compiler/parser/statements/statement_parser.py

from typing import Optional
from compiler.lexer.token_type import LmnTokenType

# Import the specialized statement parsers:
from compiler.parser.statements.function_parser import FunctionDefinitionParser
from compiler.parser.statements.if_parser import IfParser
from compiler.parser.statements.for_parser import ForParser
from compiler.parser.statements.set_parser import SetParser
from compiler.parser.statements.print_parser import PrintParser
from compiler.parser.statements.return_parser import ReturnParser

class StatementParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse_statement(self):
        token = self.parser.current_token
        if token is None:
            return None

        ttype = token.token_type

        if ttype == LmnTokenType.FUNCTION:
            # If we want to consume 'function' here:
            self.parser.advance()
            return FunctionDefinitionParser(self.parser).parse()

        elif ttype == LmnTokenType.IF:
            return IfParser(self.parser).parse()

        elif ttype == LmnTokenType.FOR:
            return ForParser(self.parser).parse()

        elif ttype == LmnTokenType.SET:
            return SetParser(self.parser).parse()

        elif ttype == LmnTokenType.PRINT:
            return PrintParser(self.parser).parse()

        elif ttype == LmnTokenType.RETURN:
            return ReturnParser(self.parser).parse()

        # Possibly other statements here: `call`, `while`, etc.

        raise SyntaxError(f"Unexpected token for statement: {ttype}")
