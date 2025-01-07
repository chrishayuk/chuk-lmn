# file: lmn/compiler/parser/expressions/function_expression_parser.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression
from lmn.compiler.parser.parser_utils import expect_token, current_token_is

logger = logging.getLogger(__name__)

class FunctionExpressionParser:
    """
    Handles inline/anonymous function expressions of the form:
        function(a, b)
            return a + b
        end

    optionally with type annotations and/or return type, e.g.:
        function(a: int, b: int): int
            return a + b
        end
    """
    def __init__(self, parent_parser, expression_parser):
        self.parser = parent_parser
        self.expr_parser = expression_parser  # if you need sub-expressions

    def parse_function_expression(self):
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

        # Parse parameters if not immediately ')'
        parameters = []
        if (self.parser.current_token 
            and self.parser.current_token.token_type != LmnTokenType.RPAREN):
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

            # Add both built-ins and user-defined as needed
            valid_types = (
                LmnTokenType.IDENTIFIER,   # e.g. "int" if your lexer calls it IDENTIFIER
                LmnTokenType.INT,
                LmnTokenType.LONG,
                LmnTokenType.FLOAT,
                LmnTokenType.DOUBLE,
                LmnTokenType.STRING_TYPE,
                LmnTokenType.JSON_TYPE,
            )
            if self.parser.current_token.token_type in valid_types:
                return_type = self.parser.current_token.value
                logger.debug("parse_function_expression: parsed return type '%s'", return_type)
                self.parser.advance()
            else:
                raise SyntaxError(
                    "Expected valid return type after ':' in inline function"
                )

        # 5) Parse function body until 'end'
        body_statements = self._parse_function_body()

        # 6) Expect 'end'
        expect_token(
            self.parser,
            LmnTokenType.END,
            "Expected 'end' after inline function body"
        )
        logger.debug("parse_function_expression: consuming 'end' token")
        self.parser.advance()  # consume 'end'

        # 7) Build & return the AST node
        anon_func = AnonymousFunctionExpression(
            parameters=parameters,
            return_type=return_type,
            body=body_statements
        )
        logger.debug(f"anonymous func: {anon_func}")

        return anon_func
    
    def _parse_parameter_list(self):
        """
        Parses zero or more parameters like:
            a, b
        or with types:
            a: int, b: float
        until we see ')'.
        """
        params = []

        logger.debug("_parse_parameter_list: starting param list parse")

        if (self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.RPAREN):
            logger.debug("_parse_parameter_list: found ')' immediately => no parameters")
            return params

        while (
            self.parser.current_token 
            and self.parser.current_token.token_type != LmnTokenType.RPAREN
        ):
            logger.debug(
                "_parse_parameter_list: current token: %s", self.parser.current_token
            )

            # 1) Expect an IDENTIFIER for param name
            ident_token = expect_token(
                self.parser, 
                LmnTokenType.IDENTIFIER, 
                "Expected parameter name"
            )
            param_name = ident_token.value
            logger.debug(
                "_parse_parameter_list: recognized param name '%s' (token: %s)",
                param_name, ident_token
            )
            self.parser.advance()  # consume the identifier

            param_type = None
            # 2) If there's a colon => parse param type
            if current_token_is(self.parser, LmnTokenType.COLON):
                logger.debug(
                    "_parse_parameter_list: found ':' after param '%s'; parsing type", 
                    param_name
                )
                self.parser.advance()  # consume ':'

                # Show EXACTLY which token is next, for debugging
                if self.parser.current_token:
                    logger.debug(
                        "_parse_parameter_list: next token is type='%s', value='%s'",
                        self.parser.current_token.token_type.name,
                        self.parser.current_token.value
                    )
                else:
                    logger.debug(
                        "_parse_parameter_list: next token is None (unexpected end of tokens?)"
                    )

                # The recognized type tokens can include IDENTIFIER if 'int' is tokenized that way
                valid_param_types = (
                    LmnTokenType.IDENTIFIER,
                    LmnTokenType.INT,
                    LmnTokenType.LONG,
                    LmnTokenType.FLOAT,
                    LmnTokenType.DOUBLE,
                    LmnTokenType.STRING_TYPE,
                    LmnTokenType.JSON_TYPE
                )
                logger.debug(
                    "_parse_parameter_list: expecting one of %s for param '%s'",
                    [t.name for t in valid_param_types],
                    param_name
                )

                # Actually parse the type token
                type_token = expect_token(
                    self.parser,
                    valid_param_types,
                    f"Expected valid type after ':' for param '{param_name}'"
                )
                param_type = type_token.value
                logger.debug(
                    "_parse_parameter_list: param '%s' has type token '%s' => '%s'",
                    param_name, type_token.token_type.name, param_type
                )
                self.parser.advance()  # consume the type token

            # 3) Append (paramName, paramType) to the list
            logger.debug(
                "_parse_parameter_list: adding param tuple (name='%s', type='%s')",
                param_name, param_type
            )
            params.append((param_name, param_type))

            # 4) If there's a comma, consume it => parse the next param
            if (
                self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                logger.debug(
                    "_parse_parameter_list: found ',' after param '%s'; continuing next param",
                    param_name
                )
                self.parser.advance()
            else:
                logger.debug(
                    "_parse_parameter_list: no comma after param '%s', likely end of param list or close paren",
                    param_name
                )
                # We let the while loop continue if not ')', or exit if next token is ')'

        logger.debug("_parse_parameter_list: finished param list => %s", params)
        return params


    def _parse_function_body(self):
        """
        Reads statements until 'end'.
        Calls statement_parser.parse_statement().
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
                    "parse_function_body got None from parse_statement(); skipping token."
                )
                self.parser.advance()

        logger.debug("parse_function_body final statements: %s", statements)
        return statements
