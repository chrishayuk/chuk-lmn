# file: lmn/compiler/parser/expressions/function_expression_parser.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression
from lmn.compiler.parser.parser_utils import expect_token, current_token_is

logger = logging.getLogger(__name__)

class FunctionExpressionParser:
    """
    Handles inline/anonymous function expressions of the form:
        function (a, b)
            return a + b
        end

    optionally with type annotations and/or return type, e.g.:
        function (a: int, b: int): int
            return a + b
        end
    """
    def __init__(self, parent_parser, expression_parser):
        """
        :param parent_parser: The main Parser object (with .current_token, .advance(), etc.)
        :param expression_parser: An instance of ExpressionParser
        """
        self.parser = parent_parser
        self.expr_parser = expression_parser  # if you need to parse sub-expressions

    def parse_function_expression(self):
        """
        Parse an inline function expression starting at 'function'.
        Example:
            function(a, b)
                return a + b
            end
        """
        # 1) Expect 'function'
        expect_token(
            self.parser, 
            LmnTokenType.FUNCTION, 
            "Expected 'function' keyword at start of inline function"
        )
        logger.debug("parse_function_expression: consuming 'function' token")
        self.parser.advance()  # consume 'function'

        # 2) Expect '(' to begin parameter list
        expect_token(
            self.parser,
            LmnTokenType.LPAREN,
            "Expected '(' after 'function'"
        )
        logger.debug("parse_function_expression: consuming '(' token")
        self.parser.advance()  # consume '('

        parameters = []
        # If not immediately ')', parse parameter list
        if self.parser.current_token and self.parser.current_token.token_type != LmnTokenType.RPAREN:
            parameters = self._parse_parameter_list()

        # 3) Expect ')'
        expect_token(
            self.parser,
            LmnTokenType.RPAREN,
            "Expected ')' after inline function parameters"
        )
        logger.debug("parse_function_expression: consuming ')' token")
        self.parser.advance()  # consume ')'

        # 4) Optional ': returnType'
        return_type = None
        if current_token_is(self.parser, LmnTokenType.COLON):
            logger.debug("parse_function_expression: found return type colon")
            self.parser.advance()  # consume ':'
            if not self.parser.current_token:
                raise SyntaxError("Expected return type after ':' in inline function")

            # Example: int, float, string, etc. Adjust as needed.
            valid_types = (
                LmnTokenType.INT,
                    LmnTokenType.LONG,
                    LmnTokenType.FLOAT,
                    LmnTokenType.DOUBLE,
                    LmnTokenType.STRING_TYPE,
                    LmnTokenType.JSON_TYPE
                # etc. add more if you have them
            )
            if self.parser.current_token.token_type in valid_types:
                return_type = self.parser.current_token.value
                logger.debug("parse_function_expression: parsed return type '%s'", return_type)
                self.parser.advance()
            else:
                raise SyntaxError("Expected valid return type after ':' in inline function")

        # 5) Parse the function body until 'end'
        body_statements = self._parse_function_body()

        # 6) Expect 'end'
        expect_token(
            self.parser,
            LmnTokenType.END,
            "Expected 'end' after inline function body"
        )
        logger.debug("parse_function_expression: consuming 'end' token")
        self.parser.advance()  # consume 'end'

        # 7) Build & return the AST node for an inline/anonymous function
        logger.debug(
            "parse_function_expression: returning AnonymousFunctionExpression with %d statements",
            len(body_statements)
        )

        # anonymous function expression
        anon_func = AnonymousFunctionExpression(
            parameters=parameters,
            return_type=return_type,
            body=body_statements
        )

        # log it
        logger.debug(f"anonymous func: {anon_func}")

        # retun
        return anon_func

    def _parse_parameter_list(self):
        """
        Parses zero or more parameters like:
            a, b
        or with types:
            a: int, b: float
        until reaching ')' or end of tokens.
        """
        params = []
        while (self.parser.current_token 
               and self.parser.current_token.token_type != LmnTokenType.RPAREN):
            # Expect an identifier for param name
            ident_token = expect_token(
                self.parser, 
                LmnTokenType.IDENTIFIER, 
                "Expected parameter name"
            )
            param_name = ident_token.value
            logger.debug("parse_function_expression: found param name '%s'", param_name)
            self.parser.advance()  # consume the identifier

            param_type = None
            # If there's a colon => parse something like "a: int"
            if current_token_is(self.parser, LmnTokenType.COLON):
                self.parser.advance()  # consume ':'
                
                valid_param_types = (
                    LmnTokenType.INT,
                    LmnTokenType.LONG,
                    LmnTokenType.FLOAT,
                    LmnTokenType.DOUBLE,
                    LmnTokenType.STRING_TYPE,
                    LmnTokenType.JSON_TYPE
                    # etc. add more as needed
                )
                type_token = expect_token(
                    self.parser,
                    valid_param_types,
                    f"Expected valid type after ':' for param '{param_name}'"
                )
                param_type = type_token.value
                logger.debug("parse_function_expression: param '%s' has type '%s'", param_name, param_type)
                self.parser.advance()  # consume the type token

            params.append((param_name, param_type))

            # If there's a comma, consume and continue
            if (self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.COMMA):
                logger.debug("parse_function_expression: found comma, continuing parameters")
                self.parser.advance()

        return params

    def _parse_function_body(self):
        """
        Keeps parsing statements until 'end'. Each iteration:
          - calls statement_parser.parse_statement()
          - if it returns None, skip or handle
        """
        statements = []

        while (
            self.parser.current_token 
            and self.parser.current_token.token_type != LmnTokenType.END
        ):
            logger.debug(
                "parse_function_body sees token: %s", 
                self.parser.current_token
            )

            stmt = self.parser.statement_parser.parse_statement()
            if stmt:
                logger.debug("parse_function_body got statement: %s", stmt)
                statements.append(stmt)
            else:
                logger.debug(
                    "parse_function_body got None from parse_statement(); "
                    "advancing the token to skip."
                )
                self.parser.advance()

        logger.debug("parse_function_body final statements: %s", statements)
        return statements
