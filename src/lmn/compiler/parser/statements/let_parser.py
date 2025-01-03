# file: lmn/compiler/parser/statements/let_parser.py

from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token, current_token_is
from lmn.compiler.ast import LetStatement, VariableExpression

class LetParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parses statements like:
            let x: int = 5
            let y
            let ratio: float
            let eVal: double = 2.718
            let typedNums: int[] = [1, 2, 3]
            let strVal: string = "Hello"
            let data: json = {"key":"val"}
            let arrOfStr: string[] = ["red","green"]
        """
        # 1) Consume the 'let' token (already current_token)
        self.parser.advance()  # move past LmnTokenType.LET

        # 2) Expect an IDENTIFIER for the variable name
        var_token = expect_token(
            self.parser,
            LmnTokenType.IDENTIFIER,
            "Expected variable name after 'let'"
        )
        self.parser.advance()  # consume the variable name token

        # 3) Check for optional ': type'
        type_annotation = None
        if current_token_is(self.parser, LmnTokenType.COLON):
            # consume ':'
            self.parser.advance()

            # Extend valid_type_tokens to include STRING_TYPE, JSON_TYPE
            valid_type_tokens = (
                LmnTokenType.INT,
                LmnTokenType.LONG,
                LmnTokenType.FLOAT,
                LmnTokenType.DOUBLE,
                LmnTokenType.STRING_TYPE,  # e.g. 'string'
                LmnTokenType.JSON_TYPE,    # e.g. 'json'
            )

            if (
                self.parser.current_token
                and self.parser.current_token.token_type in valid_type_tokens
            ):
                # This is the base type as a string (e.g. "int", "string", "json")
                type_annotation = self.parser.current_token.value
                self.parser.advance()  # consume that type keyword

                # Optional bracket pair => e.g. "string" -> "string[]"
                if (
                    self.parser.current_token
                    and self.parser.current_token.token_type == LmnTokenType.LBRACKET
                ):
                    self.parser.advance()  # consume '['
                    if not self.parser.current_token or \
                       self.parser.current_token.token_type != LmnTokenType.RBRACKET:
                        raise SyntaxError(
                            "Expected ']' for array type annotation in 'let' statement"
                        )
                    self.parser.advance()  # consume ']'

                    # Append '[]' to e.g. "int" => "int[]"
                    # or "string" => "string[]", "json" => "json[]"
                    type_annotation += "[]"

            else:
                raise SyntaxError(
                    "Expected a type keyword (int, long, float, double, string, json) after ':'"
                )

        # 4) Optional '=' <expr>
        initializer_expr = None
        if current_token_is(self.parser, LmnTokenType.EQ):
            self.parser.advance()  # consume '='
            initializer_expr = self.parser.expression_parser.parse_expression()
            if not initializer_expr:
                raise SyntaxError(
                    f"Expected an expression after 'let {var_token.value} ='"
                )

        # 5) Build and return the LetStatement node
        return LetStatement(
            variable=VariableExpression(name=var_token.value),
            expression=initializer_expr,
            type_annotation=type_annotation
        )
