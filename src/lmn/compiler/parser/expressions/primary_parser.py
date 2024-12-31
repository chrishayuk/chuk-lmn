# file: lmn/compiler/parser/expressions/primary_parser.py

from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import (
    LiteralExpression,
    FnExpression,
    VariableExpression,
)
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.parser.statements.statement_boundaries import is_statement_boundary

class PrimaryParser:
    def __init__(self, parent_parser, expr_parser):
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def parse_primary(self):
        """
        primary := 
            INT_LITERAL
          | LONG_LITERAL
          | FLOAT_LITERAL
          | DOUBLE_LITERAL
          | STRING
          | IDENTIFIER [ '(' args ')' ]
          | '(' expression ')'
          | '{' ... '}' (JSON object literal)
          | '[' ... ']' => prefer native array, fallback to JSON array
        """
        token = self.parser.current_token
        if not token:
            raise SyntaxError("Unexpected end of input in primary expression")

        if is_statement_boundary(token.token_type):
            return None

        ttype = token.token_type

        # (A) If it's '{', parse JSON object
        if ttype == LmnTokenType.LBRACE:
            return self.parse_json_object_literal()

        # (B) If it's '[', decide whether to parse native array or JSON
        if ttype == LmnTokenType.LBRACKET:
            saved_state = self.parser.save_state()

            # Optional heuristic: if we find a '{' inside the bracket range,
            # we suspect JSON objects, so parse JSON first.
            if self._bracket_contains_brace():
                try:
                    return self.parse_json_array_literal()
                except SyntaxError:
                    # revert and parse as native array
                    self.parser.restore_state(saved_state)
                    return self.parse_array_literal()
            else:
                # Default: parse native array first, fallback to JSON
                try:
                    return self.parse_array_literal()
                except SyntaxError:
                    self.parser.restore_state(saved_state)
                    return self.parse_json_array_literal()

        # (C) Numeric & string literals
        if ttype in (
            LmnTokenType.INT_LITERAL,
            LmnTokenType.LONG_LITERAL,
            LmnTokenType.FLOAT_LITERAL,
            LmnTokenType.DOUBLE_LITERAL,
            LmnTokenType.STRING
        ):
            self.parser.advance()  # consume the token
            return LiteralExpression.from_token(token)

        # (D) Identifiers => variable or function call
        if ttype == LmnTokenType.IDENTIFIER:
            var_name = token.value
            self.parser.advance()  # consume identifier

            # Check for function call syntax: name(...)
            if (
                self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.LPAREN
            ):
                self.parser.advance()  # consume '('
                args = []
                while (
                    self.parser.current_token
                    and self.parser.current_token.token_type != LmnTokenType.RPAREN
                ):
                    arg = self.expr_parser.parse_expression()
                    args.append(arg)

                    if (
                        self.parser.current_token
                        and self.parser.current_token.token_type == LmnTokenType.COMMA
                    ):
                        self.parser.advance()  # consume ','
                # Expect closing parenthesis
                self._expect(
                    LmnTokenType.RPAREN,
                    f"Expected ')' after arguments in call to '{var_name}'"
                )
                self.parser.advance()  # consume ')'

                return FnExpression(
                    name=VariableExpression(name=var_name),
                    arguments=args
                )
            
            # Simple variable reference
            return VariableExpression(name=var_name)

        # (E) Parenthesized expression => ( expr )
        if ttype == LmnTokenType.LPAREN:
            self.parser.advance()  # consume '('
            expr = self.expr_parser.parse_expression()
            self._expect(
                LmnTokenType.RPAREN,
                "Expected ')' to close grouped expression"
            )
            self.parser.advance()  # consume ')'
            return expr

        # Otherwise => error
        raise SyntaxError(
            f"Unexpected token in primary expression: {token.value} ({token.token_type})"
        )

    # -------------------------------------------------------------------------
    #  JSON Object => { ... }
    # -------------------------------------------------------------------------
    def parse_json_object_literal(self):
        """
        Parses a JSON object literal: { "key": value, ... }
        Returns JsonLiteralExpression(value=<dict>).
        """
        self.parser.advance()  # consume '{'
        obj_data = {}

        # If next token is '}', empty object
        if (
            self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.RBRACE
        ):
            self.parser.advance()  # consume '}'
            return JsonLiteralExpression(value=obj_data)

        # Otherwise parse key-value pairs
        while self.parser.current_token:
            if self.parser.current_token.token_type != LmnTokenType.STRING:
                raise SyntaxError("Expected string key in JSON object")

            key = self.parser.current_token.value
            self.parser.advance()  # consume string

            self._expect(LmnTokenType.COLON, "Expected ':' after key in JSON object")
            self.parser.advance()  # consume ':'

            # parse the value
            val = self.parse_json_value()
            obj_data[key] = val

            # If next is COMMA, continue. If '}', close object
            if (
                self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume ','
                continue
            else:
                self._expect(LmnTokenType.RBRACE, "Expected '}' or ',' in JSON object")
                self.parser.advance()  # consume '}'
                return JsonLiteralExpression(value=obj_data)

        raise SyntaxError("Unclosed JSON object literal (missing '}')")

    # -------------------------------------------------------------------------
    #  JSON Array => [ ... ]
    # -------------------------------------------------------------------------
    def parse_json_array_literal(self):
        """
        Parses a JSON array literal: [ value1, value2, ... ]
        Returns JsonLiteralExpression(value=<list>).
        """
        self.parser.advance()  # consume '['
        arr_data = []

        if (
            self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.RBRACKET
        ):
            # empty array
            self.parser.advance()  # consume ']'
            return JsonLiteralExpression(value=arr_data)

        while self.parser.current_token:
            val = self.parse_json_value()
            arr_data.append(val)

            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume ','
            else:
                self._expect(LmnTokenType.RBRACKET, "Expected ']' or ',' in JSON array")
                self.parser.advance()  # consume ']'
                return JsonLiteralExpression(value=arr_data)

        raise SyntaxError("Unclosed JSON array literal (missing ']')")

    # -------------------------------------------------------------------------
    #  parse_json_value
    # -------------------------------------------------------------------------
    def parse_json_value(self):
        """
        Parse { }, [ ], string, number, bool, or nil for JSON context.
        Returns a raw Python structure or nested JsonLiteralExpression(value=...).
        """
        token = self.parser.current_token
        if not token:
            raise SyntaxError("Unexpected end of tokens in JSON value")

        ttype = token.token_type

        if ttype == LmnTokenType.LBRACE:
            node = self.parse_json_object_literal()
            return node.value
        if ttype == LmnTokenType.LBRACKET:
            node = self.parse_json_array_literal()
            return node.value
        if ttype == LmnTokenType.STRING:
            val = token.value
            self.parser.advance()
            return val
        if ttype in (
            LmnTokenType.INT_LITERAL,
            LmnTokenType.LONG_LITERAL,
            LmnTokenType.FLOAT_LITERAL,
            LmnTokenType.DOUBLE_LITERAL
        ):
            val = token.value
            self.parser.advance()
            return val
        if ttype == LmnTokenType.TRUE:
            self.parser.advance()
            return True
        if ttype == LmnTokenType.FALSE:
            self.parser.advance()
            return False
        if ttype == LmnTokenType.NIL:
            self.parser.advance()
            return None

        raise SyntaxError(f"Unexpected token in JSON value: {token.value} ({ttype})")

    # -------------------------------------------------------------------------
    #  parse_array_literal => native array
    # -------------------------------------------------------------------------
    def parse_array_literal(self):
        """
        Parses a native array literal: [ expr1, expr2, ... ]
        Each element is a full expression, not just a JSON value.
        """
        self.parser.advance()  # consume '['
        elements = []

        if (self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.RBRACKET):
            # empty array
            self.parser.advance()  # consume ']'
            return ArrayLiteralExpression(elements=elements)

        while True:
            expr = self.expr_parser.parse_expression()
            if expr is None:
                raise SyntaxError("Expected expression inside array literal")
            elements.append(expr)

            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume ','
            else:
                self._expect(LmnTokenType.RBRACKET, "Expected ']' at end of array literal")
                self.parser.advance()  # consume ']'
                break

        return ArrayLiteralExpression(elements=elements)

    # -------------------------------------------------------------------------
    #  _expect
    # -------------------------------------------------------------------------
    def _expect(self, token_type, message):
        if (
            not self.parser.current_token
            or self.parser.current_token.token_type != token_type
        ):
            raise SyntaxError(message)
        return self.parser.current_token

    # -------------------------------------------------------------------------
    #  _bracket_contains_brace (optional heuristic)
    # -------------------------------------------------------------------------
    def _bracket_contains_brace(self) -> bool:
        """
        Scan tokens from the current '[' to the matching ']' at same bracket depth.
        If we see a '{' at that depth, return True => likely JSON objects inside.
        """
        depth = 0
        pos = self.parser.current_pos
        tokens = self.parser.tokens

        while pos < len(tokens):
            t = tokens[pos]
            if t.token_type == LmnTokenType.LBRACKET:
                depth += 1
            elif t.token_type == LmnTokenType.RBRACKET:
                depth -= 1
                if depth <= 0:
                    # Reached the matching ']'
                    break
            # If we see a '{' while bracket depth > 0, we suspect JSON
            elif t.token_type == LmnTokenType.LBRACE and depth > 0:
                return True

            pos += 1

        return False
