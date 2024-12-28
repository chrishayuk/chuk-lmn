# function_definition_parser.py

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
        """
        # 'function' is already consumed in statement_parser, so we expect an IDENTIFIER next.
        func_token = self._expect(
            LmnTokenType.IDENTIFIER,
            "Expected function name after 'function'"
        )
        func_name = func_token.value
        self.parser.advance()  # consume function name

        self._expect(LmnTokenType.LPAREN, "Expected '(' after function name")
        self.parser.advance()  # consume '('

        # --------------------------------------------------
        # Parse parameter list (handling optional types).
        # --------------------------------------------------
        params = self._parse_parameters()

        self._expect(LmnTokenType.RPAREN, "Expected ')' after parameters")
        self.parser.advance()  # consume ')'

        # --------------------------------------------------
        # Parse optional return type (e.g. ": int") 
        # --------------------------------------------------
        return_type = None
        if (
            self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.COLON
        ):
            # Consume ':'
            self.parser.advance()

            # Accept built-in type tokens AND IDENTIFIER
            valid_type_tokens = [
                LmnTokenType.IDENTIFIER,
                LmnTokenType.INT,
                LmnTokenType.LONG,
                LmnTokenType.FLOAT,
                LmnTokenType.DOUBLE,
            ]

            if (
                not self.parser.current_token
                or self.parser.current_token.token_type not in valid_type_tokens
            ):
                raise SyntaxError("Expected return type after ':' in function definition")

            return_type_token = self.parser.current_token
            return_type = return_type_token.value  # e.g., "int", "float", "MyType"
            self.parser.advance()  # consume the return-type token

        # Parse the body until 'end'.
        body_stmts = self._parse_block(until_tokens=[LmnTokenType.END])

        self._expect(LmnTokenType.END, "Expected 'end' after function body")
        self.parser.advance()  # consume 'end'

        return FunctionDefinition(
            name=func_name,
            params=params,
            body=body_stmts,
            return_type=return_type  # Only if your AST node has this field
        )


    def _parse_parameters(self):
        """
        Parses zero or more parameters, e.g.:
           a, b: string, c, ...
        where each parameter is:
           <name> ( ':' <type> )?
        Returns a list of `FunctionParameter`.
        """
        params = []

        # If we see a right-parenthesis here, it means zero parameters.
        if self.parser.current_token.token_type == LmnTokenType.RPAREN:
            return params

        while True:
            param_token = self._expect(
                LmnTokenType.IDENTIFIER,
                "Expected parameter name"
            )
            param_name = param_token.value
            self.parser.advance()  # consume the parameter name

            # Optional type annotation
            param_type = None
            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COLON
            ):
                self.parser.advance()  # consume ':'

                # Accept built-in type tokens AND IDENTIFIER
                valid_type_tokens = [
                    LmnTokenType.IDENTIFIER,
                    LmnTokenType.INT,
                    LmnTokenType.LONG,
                    LmnTokenType.FLOAT,
                    LmnTokenType.DOUBLE,
                ]

                if (
                    not self.parser.current_token
                    or self.parser.current_token.token_type not in valid_type_tokens
                ):
                    raise SyntaxError(
                        f"Expected type after ':' for param '{param_name}'"
                    )

                type_token = self.parser.current_token
                param_type = type_token.value  # e.g. 'int', 'float', ...
                self.parser.advance()  # consume the type token

            # Create the FunctionParameter
            function_param = FunctionParameter(
                name=param_name,
                type_annotation=param_type
            )
            params.append(function_param)

            # If next token is a comma, consume it and parse the next param
            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume comma
            else:
                break

        return params

    def _parse_block(self, until_tokens):
        """
        Reads statements until one of the tokens in `until_tokens` is encountered.
        Skips COMMENT/NEWLINE tokens if needed.
        """
        statements = []
        while (
            self.parser.current_token
            and self.parser.current_token.token_type not in until_tokens
        ):

            # Skip COMMENT, NEWLINE if you allow blank lines or comments
            if self.parser.current_token.token_type in (LmnTokenType.COMMENT, LmnTokenType.NEWLINE):
                self.parser.advance()
                continue

            stmt = self.parser.statement_parser.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # If parse_statement returned None, consume a token or break
                self.parser.advance()

        return statements

    def _expect(self, token_type, err_msg):
        """
        Verifies that current_token is `token_type`.
        Does NOT advance; do that in your code as needed.
        """
        if (
            not self.parser.current_token
            or self.parser.current_token.token_type != token_type
        ):
            raise SyntaxError(err_msg)
        return self.parser.current_token
