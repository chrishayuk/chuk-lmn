# file: lmn/compiler/parser/statements/let_parser.py

import logging

from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token, current_token_is
from lmn.compiler.ast import LetStatement, VariableExpression

logger = logging.getLogger(__name__)

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

        Also supports inline functions if ExpressionParser can handle them:
            let sum_func = function(a, b)
                return a + b
            end
        """
        logger.debug("Starting parse of 'let' statement. Current token: %r", self.parser.current_token)

        # 1) Consume the 'let' token (already current_token)
        self.parser.advance()  # move past LmnTokenType.LET
        logger.debug("Consumed 'let'. Next token: %r", self.parser.current_token)

        # 2) Expect an IDENTIFIER for the variable name
        var_token = expect_token(
            self.parser,
            LmnTokenType.IDENTIFIER,
            "Expected variable name after 'let'"
        )
        logger.debug("Found variable name token: %r", var_token)
        self.parser.advance()  # consume the variable name token
        logger.debug("After consuming variable name, current token: %r", self.parser.current_token)

        # 3) Check for optional ': type'
        type_annotation = None
        if current_token_is(self.parser, LmnTokenType.COLON):
            # consume ':'
            self.parser.advance()
            logger.debug("Detected ':' for type annotation.")

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
                logger.debug("Base type annotation: %r", type_annotation)
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

                    type_annotation += "[]"
                    logger.debug("Detected array type annotation, now: %r", type_annotation)
            else:
                raise SyntaxError(
                    "Expected a type keyword (int, long, float, double, string, json) after ':'"
                )

        # 4) Optional '=' <expr>
        initializer_expr = None
        if current_token_is(self.parser, LmnTokenType.EQ):
            self.parser.advance()  # consume '='
            logger.debug("Detected '=' for initializer expression.")
            initializer_expr = self.parser.expression_parser.parse_expression()
            if not initializer_expr:
                raise SyntaxError(
                    f"Expected an expression after 'let {var_token.value} ='"
                )
            logger.debug("Parsed initializer expression: %r", initializer_expr)

        # 5) Build and return the LetStatement node
        let_statement = LetStatement(
            variable=VariableExpression(name=var_token.value),
            expression=initializer_expr,
            type_annotation=type_annotation
        )
        logger.debug("Constructed LetStatement node: %r", let_statement)
        return let_statement
