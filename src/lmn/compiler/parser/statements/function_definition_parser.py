# file: lmn/compiler/parser/statements/function_definition_parser.py

from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.statements.function_definition import FunctionDefinition
from lmn.compiler.ast.statements.function_parameter import FunctionParameter

class FunctionDefinitionParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parses something like:

        function sum(a: int, b: int): int
            let result: int
            result = a + b
            return result
        end

        or with no typed return:

        function sum(a: int, b: int)
            ...
        end
        """
        # 'function' is already consumed in statement_parser, so expect IDENTIFIER next
        func_token = self._expect(
            LmnTokenType.IDENTIFIER,
            "Expected function name after 'function'"
        )
        func_name = func_token.value
        self.parser.advance()  # consume function name

        self._expect(LmnTokenType.LPAREN, "Expected '(' after function name")
        self.parser.advance()  # consume '('

        # Parse parameters
        params = self._parse_parameters()

        self._expect(LmnTokenType.RPAREN, "Expected ')' after parameters")
        self.parser.advance()  # consume ')'

        # ---------------------------------------
        # Parse optional return type: e.g. ": int"
        # ---------------------------------------
        return_type = None
        if (
            self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.COLON
        ):
            self.parser.advance()  # consume ':'

            # Accept built-in type tokens, plus IDENTIFIER, plus FUNCTION
            valid_type_tokens = [
                LmnTokenType.IDENTIFIER,
                LmnTokenType.INT,
                LmnTokenType.LONG,
                LmnTokenType.FLOAT,
                LmnTokenType.DOUBLE,
                LmnTokenType.STRING_TYPE,
                LmnTokenType.JSON_TYPE,
                LmnTokenType.FUNCTION  # for "function" as a type
            ]
            if (
                not self.parser.current_token
                or self.parser.current_token.token_type not in valid_type_tokens
            ):
                raise SyntaxError("Expected return type after ':' in function definition")

            return_type_token = self.parser.current_token
            return_type = return_type_token.value  # e.g. "int", "function", ...
            self.parser.advance()  # consume that token

        # Parse the body until 'end'
        body_stmts = self._parse_block(until_tokens=[LmnTokenType.END])

        self._expect(LmnTokenType.END, "Expected 'end' after function body")
        self.parser.advance()  # consume 'end'

        return FunctionDefinition(
            name=func_name,
            params=params,
            body=body_stmts,
            return_type=return_type
        )

    def _parse_parameters(self):
        """
        Parses zero or more parameters, e.g.: 
          a, b: string, c: int[], ...
        Returns a list of `FunctionParameter`.
        """
        params = []

        # If the next token is ')', we have zero parameters
        if self.parser.current_token.token_type == LmnTokenType.RPAREN:
            return params

        while True:
            # 1) Expect an IDENTIFIER for the param name
            param_token = self._expect(
                LmnTokenType.IDENTIFIER,
                "Expected parameter name"
            )
            param_name = param_token.value
            self.parser.advance()  # consume param name

            param_type = None

            # 2) Optional ': type'
            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COLON
            ):
                self.parser.advance()  # consume ':'

                # Now we expect either built-in type or IDENTIFIER or FUNCTION
                valid_type_tokens = [
                    LmnTokenType.IDENTIFIER,
                    LmnTokenType.INT,
                    LmnTokenType.LONG,
                    LmnTokenType.FLOAT,
                    LmnTokenType.DOUBLE,
                    LmnTokenType.FUNCTION  # in case you want param : function
                ]
                if (
                    not self.parser.current_token
                    or self.parser.current_token.token_type not in valid_type_tokens
                ):
                    raise SyntaxError(
                        f"Expected type after ':' for param '{param_name}'"
                    )

                type_token = self.parser.current_token
                param_type = type_token.value
                self.parser.advance()  # consume the type token

                # 3) Check if the next tokens are '[ ]' for an array type
                if (
                    self.parser.current_token
                    and self.parser.current_token.token_type == LmnTokenType.LBRACKET
                ):
                    # Must match a following ']'
                    self.parser.advance()  # consume '['
                    if (
                        not self.parser.current_token
                        or self.parser.current_token.token_type != LmnTokenType.RBRACKET
                    ):
                        raise SyntaxError("Expected ']' for array type annotation")
                    self.parser.advance()  # consume ']'

                    # Append '[]' to the type
                    param_type += "[]"

            # Create the FunctionParameter
            function_param = FunctionParameter(
                name=param_name,
                type_annotation=param_type
            )
            params.append(function_param)

            # If next token is a comma, consume it => parse next param
            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume ','
            else:
                break

        return params

    def _parse_block(self, until_tokens):
        """
        Reads statements until one of the tokens in `until_tokens`.
        Skips COMMENT/NEWLINE if needed.
        FLATTENS multiple statements if parse_statement() returns a list.
        """
        statements = []
        while (
            self.parser.current_token
            and self.parser.current_token.token_type not in until_tokens
        ):
            # skip blank lines / comments
            if self.parser.current_token.token_type in (
                LmnTokenType.COMMENT,
                LmnTokenType.NEWLINE
            ):
                self.parser.advance()
                continue

            stmt_or_stmts = self.parser.statement_parser.parse_statement()
            if stmt_or_stmts:
                # If parse_statement() returned multiple statements, flatten them
                if isinstance(stmt_or_stmts, list):
                    statements.extend(stmt_or_stmts)
                else:
                    statements.append(stmt_or_stmts)
            else:
                # If parse_statement returned None => likely invalid token
                # We'll just advance to avoid an infinite loop
                self.parser.advance()

        return statements

    def _expect(self, token_type, err_msg):
        """
        Verifies that current_token is `token_type`.
        Does NOT advance.
        """
        if (
            not self.parser.current_token
            or self.parser.current_token.token_type != token_type
        ):
            raise SyntaxError(err_msg)
        return self.parser.current_token
