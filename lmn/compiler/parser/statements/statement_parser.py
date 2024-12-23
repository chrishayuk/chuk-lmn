# compiler/parser/statements/statement_parser.py
from typing import Optional
from compiler.lexer.token_type import LmnTokenType
from compiler.parser.statements.function_parser import FunctionDefinitionParser
from compiler.parser.statements.if_parser import IfParser
from compiler.parser.statements.for_parser import ForParser
from compiler.parser.statements.set_parser import SetParser
from compiler.parser.statements.print_parser import PrintParser
from compiler.parser.statements.return_parser import ReturnParser

class StatementParser:
    def __init__(self, parent_parser):
        # set the parent parser
        self.parser = parent_parser

    def parse_statement(self):
        # check if the current token is a statement keyword
        token = self.parser.current_token

        # check if the current token is None
        if token is None:
            # return None if the current token is None
            return None
        
        # get the token type
        ttype = token.token_type

        # check if the token type is a statement keyword
        if ttype == LmnTokenType.FUNCTION:
            # If we want to consume 'function' here:
            self.parser.advance()
            return FunctionDefinitionParser(self.parser).parse()
        
        # check if the current token is an if statement keyword
        elif ttype == LmnTokenType.IF:
            # parse the if statement
            return IfParser(self.parser).parse()

        elif ttype == LmnTokenType.FOR:
            # parse the for statement
            return ForParser(self.parser).parse()

        elif ttype == LmnTokenType.SET:
            # parse the set statement
            return SetParser(self.parser).parse()

        elif ttype == LmnTokenType.PRINT:
            # parse the print statement
            return PrintParser(self.parser).parse()

        elif ttype == LmnTokenType.RETURN:
            # parse the run statement
            return ReturnParser(self.parser).parse()

        # Possibly other statements here: `call`

        # unexpected token
        raise SyntaxError(f"Unexpected token for statement: {ttype}")
