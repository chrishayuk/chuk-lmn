# lmn/compiler/parser/statements/block_parser.py
from lmn.compiler.ast.statements.block_statement import BlockStatement
from lmn.compiler.lexer.token_type import LmnTokenType

class BlockParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parses a block of statements between 'begin' and 'end', like:
        
        begin
            let x: int
            x = 42
            print x
        end
        
        Note: Expects 'begin' token to already be consumed by the statement parser.
        """
        # Already have 'begin' here, so consume it
        self.parser.advance()
        
        statements = []
        
        while self.parser.current_token is not None:
            token = self.parser.current_token
            
            # Check for end of block
            if token.token_type == LmnTokenType.END:
                self.parser.advance()  # consume 'end'
                return BlockStatement(statements=statements)
                
            # Skip comments and newlines
            if token.token_type in (LmnTokenType.COMMENT, LmnTokenType.NEWLINE):
                self.parser.advance()
                continue
                
            # Try to parse a statement
            stmt = self.parser.statement_parser.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # If parse_statement returned None, advance to avoid infinite loop
                self.parser.advance()
                
        # If we get here, we never found the END token
        raise SyntaxError("Expected 'end' to close block")