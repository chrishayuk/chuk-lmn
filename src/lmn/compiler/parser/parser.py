# lmn/compiler/parser/parser.py
from typing import List, Optional
from lmn.compiler.lexer.token import Token
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.program import Program
from lmn.compiler.parser.statements.statement_parser import StatementParser
from lmn.compiler.parser.expressions.expression_parser import ExpressionParser


class Parser:
    def __init__(self, tokens: List[Token]):
        """
        The main Parser class, responsible for orchestrating the parse of a token list
        into a high-level Program AST. 
        It delegates statement-specific parsing to StatementParser 
        and expression-level parsing to ExpressionParser.
        """
        self.tokens = tokens
        self.current_pos = 0
        self.current_token: Optional[Token] = tokens[0] if tokens else None

        # Helpers for parsing statements and expressions
        self.statement_parser = StatementParser(self)
        self.expression_parser = ExpressionParser(self)

    def advance(self):
        """
        Moves to the next token (if any). 
        Sets current_token to None if we pass the end of the list.
        """
        self.current_pos += 1
        if self.current_pos < len(self.tokens):
            self.current_token = self.tokens[self.current_pos]
        else:
            self.current_token = None

    def peek(self, offset: int = 1) -> Optional[Token]:
        """
        Returns the token at (current_pos + offset), or None if out of range.
        By default, offset=1 gives you the next token beyond current_token.
        """
        pos = self.current_pos + offset
        if 0 <= pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def parse(self) -> Program:
        """
        Parses the list of tokens into a Program node. 
        - Skips COMMENT and NEWLINE tokens as they are not meaningful statements.
        - Delegates statement parsing to the StatementParser.
        - If statement_parser returns None, we advance one token to avoid infinite loops.
        """
        program = Program()

        while self.current_token is not None:
            # Skip COMMENT and NEWLINE to avoid extra statements for blank lines
            if self.current_token.token_type in (LmnTokenType.COMMENT, LmnTokenType.NEWLINE):
                self.advance()
                continue

            # Attempt to parse a statement
            stmt = self.statement_parser.parse_statement()
            if stmt:
                # If we got a valid statement, add it to the Program
                program.add_statement(stmt)
            else:
                # If parse_statement() returned None, consume the current token
                # to avoid an infinite loop
                self.advance()

        return program
