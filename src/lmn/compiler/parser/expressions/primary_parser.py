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
            | '[' ... ']' => first attempt JSON array, fallback to native array literal
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

            # (B) If it's '[', first try JSON array, fallback to native array
            if ttype == LmnTokenType.LBRACKET:
                saved_state = self.parser.save_state()
                try:
                    # Attempt strict JSON parse
                    return self.parse_json_array_literal()
                except SyntaxError:
                    # If JSON parse fails, revert to '['
                    self.parser.restore_state(saved_state)
                    # Then parse as a native array of expressions
                    return self.parse_array_literal()

            # (C) Numeric Literals
            if ttype in (
                LmnTokenType.INT_LITERAL,
                LmnTokenType.LONG_LITERAL,
                LmnTokenType.FLOAT_LITERAL,
                LmnTokenType.DOUBLE_LITERAL,
                LmnTokenType.STRING
            ):
                self.parser.advance()  # consume the token
                return LiteralExpression.from_token(token)

            # (D) String Literal
            if ttype == LmnTokenType.STRING:
                self.parser.advance()
                return LiteralExpression(value=token.value)

            # (E) Identifiers => variable or function call
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

                        # Handle argument separator
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

            # (F) Parenthesized expression => ( expr )
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
    # JSON Object => { ... }
    # -------------------------------------------------------------------------
    def parse_json_object_literal(self):
        """
        Parses a JSON object literal: { "key": value, ... }
        Returns JsonLiteralExpression(value=<dict>).
        """
        # Current token should be LBRACE => consume it
        self.parser.advance()  # consume '{'

        obj_data = {}

        # If next token is '}', it's an empty object
        if (
            self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.RBRACE
        ):
            self.parser.advance()  # consume '}'
            return JsonLiteralExpression(value=obj_data)

        # Otherwise parse key-value pairs
        while self.parser.current_token:
            # 1) Expect STRING for key
            if self.parser.current_token.token_type != LmnTokenType.STRING:
                raise SyntaxError("Expected string key in JSON object")

            key = self.parser.current_token.value
            self.parser.advance()  # consume the string

            # 2) Expect COLON
            self._expect(LmnTokenType.COLON, "Expected ':' after key in JSON object")
            self.parser.advance()  # consume ':'

            # 3) Parse the value (could be object, array, string, number, bool, nil, etc.)
            val = self.parse_json_value()
            obj_data[key] = val

            # 4) If next is COMMA, continue. If next is '}', close object
            if (
                self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume ','
                continue
            else:
                # Must be '}' => done
                self._expect(LmnTokenType.RBRACE, "Expected '}' or ',' in JSON object")
                self.parser.advance()  # consume '}'
                return JsonLiteralExpression(value=obj_data)

        # If we exit loop => ran out of tokens
        raise SyntaxError("Unclosed JSON object literal (missing '}')")

    # -------------------------------------------------------------------------
    # JSON Array => [ ... ]
    # -------------------------------------------------------------------------
    def parse_json_array_literal(self):
        """
        Parses a JSON array literal: [ value1, value2, ... ]
        Returns JsonLiteralExpression(value=<list>).
        """
        # Current token should be LBRACKET => consume it
        self.parser.advance()  # consume '['
        arr_data = []

        # If next token is ']', it's an empty array
        if (
            self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.RBRACKET
        ):
            self.parser.advance()  # consume ']'
            return JsonLiteralExpression(value=arr_data)

        # Otherwise parse elements
        while self.parser.current_token:
            val = self.parse_json_value()
            arr_data.append(val)

            # Check next token for ',' or ']'
            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume ','
                continue
            else:
                # Must be ']'
                self._expect(LmnTokenType.RBRACKET, "Expected ']' or ',' in JSON array")
                self.parser.advance()  # consume ']'
                return JsonLiteralExpression(value=arr_data)

        raise SyntaxError("Unclosed JSON array literal (missing ']')")

    # -------------------------------------------------------------------------
    # parse_json_value:
    #    parse either an object, array, string, number, boolean, or nil
    # -------------------------------------------------------------------------
    def parse_json_value(self):
        """
        Helper used inside object/array parsing for the 'value' part.
        Returns a raw Python structure (dict, list, str, int, float, bool, None)
        or nested JsonLiteralExpression(value=...).
        
        Alternatively, we can parse as a sub-expression, but for pure JSON,
        we'll keep it strict: { }, [ ], string, number, true, false, nil.
        """
        token = self.parser.current_token
        if not token:
            raise SyntaxError("Unexpected end of tokens in JSON value")

        ttype = token.token_type

        # JSON object => parse object, but then .value
        if ttype == LmnTokenType.LBRACE:
            node = self.parse_json_object_literal()
            return node.value  # store dict directly

        # JSON array => parse array, but then .value
        if ttype == LmnTokenType.LBRACKET:
            node = self.parse_json_array_literal()
            return node.value  # store list directly

        # string
        if ttype == LmnTokenType.STRING:
            val = token.value
            self.parser.advance()
            return val

        # number
        if ttype in (
            LmnTokenType.INT_LITERAL,
            LmnTokenType.LONG_LITERAL,
            LmnTokenType.FLOAT_LITERAL,
            LmnTokenType.DOUBLE_LITERAL
        ):
            val = token.value
            self.parser.advance()
            return val

        # boolean true/false
        if ttype == LmnTokenType.TRUE:
            self.parser.advance()
            return True

        if ttype == LmnTokenType.FALSE:
            self.parser.advance()
            return False

        # nil => None (if 'null' => LmnTokenType.NIL)
        if ttype == LmnTokenType.NIL:
            self.parser.advance()
            return None

        raise SyntaxError(f"Unexpected token in JSON value: {token.value} ({ttype})")
    
    def parse_array_literal(self):
        """
        Parses a native array literal: [ expr1, expr2, ... ]
        Each element is a full expression, not just a JSON value.
        """
        self.parser.advance()  # consume '['
        elements = []

        # If next token is ']', empty array
        if (self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.RBRACKET):
            self.parser.advance()  # consume ']'
            return ArrayLiteralExpression(elements=elements)

        while True:
            # parse any expression
            expr = self.expr_parser.parse_expression()
            if expr is None:
                raise SyntaxError("Expected expression inside array literal")
            elements.append(expr)

            # Check if next token is ',' => parse more, else expect ']'
            if (self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA):
                self.parser.advance()  # consume ','
            else:
                # Must be RBRACKET => end
                self._expect(LmnTokenType.RBRACKET, "Expected ']' at end of array literal")
                self.parser.advance()  # consume ']'
                break

        return ArrayLiteralExpression(elements=elements)


    def _expect(self, token_type, message):
        """
        Verifies current token is of expected type or raises SyntaxError.
        """
        if (
            not self.parser.current_token
            or self.parser.current_token.token_type != token_type
        ):
            raise SyntaxError(message)
        return self.parser.current_token
