# lmn/compiler/parser/statements/statement_parser.py
from typing import Optional
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.statements.assignment_parser import AssignmentParser
from lmn.compiler.parser.statements.function_definition_parser import FunctionDefinitionParser
from lmn.compiler.parser.statements.if_parser import IfParser
from lmn.compiler.parser.statements.for_parser import ForParser
from lmn.compiler.parser.statements.let_parser import LetParser
from lmn.compiler.parser.statements.print_parser import PrintParser
from lmn.compiler.parser.statements.return_parser import ReturnParser

class StatementParser:
    def __init__(self, parent_parser):
        """
        :param parent_parser: reference to the main Parser instance
        """
        self.parser = parent_parser

    def parse_statement(self):
        """
        Attempts to parse a single statement based on the current token type.

        - function -> FunctionDefinitionParser
        - identifier -> AssignmentParser
        - if -> IfParser
        - for -> ForParser
        - let -> LetParser
        - print -> PrintParser
        - return -> ReturnParser
        - otherwise -> SyntaxError
        """
        token = self.parser.current_token

        # If we've run out of tokens
        if token is None:
            return None
        
        ttype = token.token_type

        # Dispatch based on the token type
        if ttype == LmnTokenType.FUNCTION:
            # Already have 'function' here, so consume it
            self.parser.advance()
            return FunctionDefinitionParser(self.parser).parse()
        
        elif ttype == LmnTokenType.IDENTIFIER:
            # e.g. myVar = 123
            return AssignmentParser(self.parser).parse()
        
        elif ttype == LmnTokenType.IF:
            return IfParser(self.parser).parse()

        elif ttype == LmnTokenType.FOR:
            return ForParser(self.parser).parse()

        elif ttype == LmnTokenType.LET:
            return LetParser(self.parser).parse()

        elif ttype == LmnTokenType.PRINT:
            return PrintParser(self.parser).parse()

        elif ttype == LmnTokenType.RETURN:
            return ReturnParser(self.parser).parse()

        # Possibly other statements here: call, break, etc.

        # If none of the recognized statement tokens matched
        raise SyntaxError(f"Unexpected token for statement: {ttype}")
