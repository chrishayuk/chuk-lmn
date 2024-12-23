# lmn/compiler/parser/parser.py
from typing import List, Optional
from lmn.compiler.lexer.token import Token
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.program import Program
from lmn.compiler.parser.statements.statement_parser import StatementParser
from lmn.compiler.parser.expressions.expression_parser import ExpressionParser

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_pos = 0
        self.current_token: Optional[Token] = tokens[0] if tokens else None
        # Create helper parsers
        self.statement_parser = StatementParser(self)
        self.expression_parser = ExpressionParser(self)

    def advance(self):
        self.current_pos += 1
        if self.current_pos < len(self.tokens):
            self.current_token = self.tokens[self.current_pos]
        else:
            self.current_token = None

    def peek(self) -> Optional[Token]:
        next_pos = self.current_pos + 1
        if next_pos < len(self.tokens):
            return self.tokens[next_pos]
        return None

    def parse(self) -> Program:
        program = Program()

        while self.current_token is not None:
            # skip comments
            if self.current_token.token_type == LmnTokenType.COMMENT:
                self.advance()
                continue

            # parse a statement using statement_parser
            stmt = self.statement_parser.parse_statement()
            if stmt:
                program.add_statement(stmt)
            else:
                self.advance()

        return program
