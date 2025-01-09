# file: lmn/compiler/parser/expressions/primary_parser.py

import logging

from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import (
    LiteralExpression,
    FnExpression,
    VariableExpression,
)
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.parser.statements.statement_boundaries import is_statement_boundary

logger = logging.getLogger(__name__)

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
            logger.debug("PrimaryParser: No current token => end of input in primary expression")
            raise SyntaxError("Unexpected end of input in primary expression")

        logger.debug(f"PrimaryParser: Current token => {token}")

        # Reject statement-only tokens (break, continue, return, etc.)
        if token.token_type in {
            LmnTokenType.BREAK, 
            LmnTokenType.CONTINUE, 
            LmnTokenType.RETURN
        }:
            logger.error(f"PrimaryParser: Found statement-only token in primary expression => {token}")
            raise SyntaxError(f"Unexpected token in primary expression: {token.value} ({token.token_type})")

        # Check for statement boundary
        if is_statement_boundary(token.token_type):
            logger.debug(f"PrimaryParser: Detected statement boundary token => {token}. Returning None.")
            return None

        ttype = token.token_type

        # (A) If it's '{', parse JSON object
        if ttype == LmnTokenType.LBRACE:
            logger.debug("PrimaryParser: Detected '{'. Parsing JSON object literal.")
            return self.parse_json_object_literal()

        # (B) If it's '[', decide whether to parse native array or JSON
        if ttype == LmnTokenType.LBRACKET:
            logger.debug("PrimaryParser: Detected '['. Checking whether to parse array or JSON.")
            saved_state = self.parser.save_state()

            # Optional heuristic: if we find a '{' inside the bracket range,
            # we suspect JSON objects, so parse JSON first.
            if self._bracket_contains_brace():
                logger.debug("PrimaryParser: Detected '{' inside bracket. Attempting JSON array first.")
                try:
                    return self.parse_json_array_literal()
                except SyntaxError:
                    logger.debug("PrimaryParser: Failed JSON array parse. Reverting to array literal.")
                    self.parser.restore_state(saved_state)
                    return self.parse_array_literal()
            else:
                # Default: parse native array first, fallback to JSON
                logger.debug("PrimaryParser: Attempting native array parse first.")
                try:
                    return self.parse_array_literal()
                except SyntaxError:
                    logger.debug("PrimaryParser: Failed native array parse. Reverting to JSON array.")
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
            logger.debug(f"PrimaryParser: Detected literal token => {token}")
            self.parser.advance()  # consume the token
            literal_expr = LiteralExpression.from_token(token)
            logger.debug(f"PrimaryParser: Created LiteralExpression => {literal_expr}")
            return literal_expr

        # (D) Identifiers => variable or function call
        if ttype == LmnTokenType.IDENTIFIER:
            var_name = token.value
            logger.debug(f"PrimaryParser: Detected IDENTIFIER => {var_name}")
            self.parser.advance()  # consume identifier

            # Check for function call syntax: name(...)
            if (
                self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.LPAREN
            ):
                logger.debug("PrimaryParser: Detected '(' after identifier => Parsing function call.")
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
                        logger.debug("PrimaryParser: Detected comma => continuing function call args.")
                        self.parser.advance()  # consume ','
                # Expect closing parenthesis
                self._expect(
                    LmnTokenType.RPAREN,
                    f"Expected ')' after arguments in call to '{var_name}'"
                )
                self.parser.advance()  # consume ')'

                fn_expr = FnExpression(
                    name=VariableExpression(name=var_name),
                    arguments=args
                )
                logger.debug(f"PrimaryParser: Created FnExpression => {fn_expr}")
                return fn_expr
            
            # Simple variable reference
            variable_expr = VariableExpression(name=var_name)
            logger.debug(f"PrimaryParser: Created VariableExpression => {variable_expr}")
            return variable_expr

        # (E) Parenthesized expression => ( expr )
        if ttype == LmnTokenType.LPAREN:
            logger.debug("PrimaryParser: Detected '('. Parsing parenthesized expression.")
            self.parser.advance()  # consume '('
            expr = self.expr_parser.parse_expression()
            self._expect(
                LmnTokenType.RPAREN,
                "Expected ')' to close grouped expression"
            )
            self.parser.advance()  # consume ')'
            logger.debug(f"PrimaryParser: Completed parenthesized expression => {expr}")
            return expr

        # Otherwise => error
        logger.error(f"PrimaryParser: Unexpected token in primary expression => {token}")
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
        logger.debug("PrimaryParser: Parsing JSON object literal.")
        self.parser.advance()  # consume '{'
        obj_data = {}

        # If next token is '}', empty object
        if (
            self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.RBRACE
        ):
            logger.debug("PrimaryParser: Detected empty JSON object ({}).")
            self.parser.advance()  # consume '}'
            return JsonLiteralExpression(value=obj_data)

        # Otherwise parse key-value pairs
        while self.parser.current_token:
            if self.parser.current_token.token_type != LmnTokenType.STRING:
                logger.error("PrimaryParser: Expected string key in JSON object.")
                raise SyntaxError("Expected string key in JSON object")

            key = self.parser.current_token.value
            logger.debug(f"PrimaryParser: JSON object key => {key}")
            self.parser.advance()  # consume string

            self._expect(LmnTokenType.COLON, "Expected ':' after key in JSON object")
            self.parser.advance()  # consume ':'

            # parse the value
            val = self.parse_json_value()
            obj_data[key] = val
            logger.debug(f"PrimaryParser: JSON object pair => {key}: {val}")

            # If next is COMMA, continue. If '}', close object
            if (
                self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                logger.debug("PrimaryParser: Detected ',' => continuing JSON object parsing.")
                self.parser.advance()  # consume ','
                continue
            else:
                self._expect(LmnTokenType.RBRACE, "Expected '}' or ',' in JSON object")
                self.parser.advance()  # consume '}'
                json_expr = JsonLiteralExpression(value=obj_data)
                logger.debug(f"PrimaryParser: Completed JSON object => {json_expr}")
                return json_expr

        logger.error("PrimaryParser: Unclosed JSON object literal (missing '}').")
        raise SyntaxError("Unclosed JSON object literal (missing '}')")

    # -------------------------------------------------------------------------
    #  JSON Array => [ ... ]
    # -------------------------------------------------------------------------
    def parse_json_array_literal(self):
        """
        Parses a JSON array literal: [ value1, value2, ... ]
        Returns JsonLiteralExpression(value=<list>).
        """
        logger.debug("PrimaryParser: Parsing JSON array literal.")
        self.parser.advance()  # consume '['
        arr_data = []

        if (
            self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.RBRACKET
        ):
            # empty array
            logger.debug("PrimaryParser: Detected empty JSON array ([]).")
            self.parser.advance()  # consume ']'
            return JsonLiteralExpression(value=arr_data)

        while self.parser.current_token:
            val = self.parse_json_value()
            arr_data.append(val)
            logger.debug(f"PrimaryParser: JSON array element => {val}")

            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                logger.debug("PrimaryParser: Detected ',' => continuing JSON array parsing.")
                self.parser.advance()  # consume ','
            else:
                self._expect(LmnTokenType.RBRACKET, "Expected ']' or ',' in JSON array")
                self.parser.advance()  # consume ']'
                json_arr_expr = JsonLiteralExpression(value=arr_data)
                logger.debug(f"PrimaryParser: Completed JSON array => {json_arr_expr}")
                return json_arr_expr

        logger.error("PrimaryParser: Unclosed JSON array literal (missing ']').")
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
            logger.error("PrimaryParser: Unexpected end of tokens in JSON value.")
            raise SyntaxError("Unexpected end of tokens in JSON value")

        ttype = token.token_type
        logger.debug(f"PrimaryParser: Parsing JSON value => {token}")

        if ttype == LmnTokenType.LBRACE:
            node = self.parse_json_object_literal()
            return node.value
        if ttype == LmnTokenType.LBRACKET:
            node = self.parse_json_array_literal()
            return node.value
        if ttype == LmnTokenType.STRING:
            val = token.value
            logger.debug(f"PrimaryParser: JSON string value => {val}")
            self.parser.advance()
            return val
        if ttype in (
            LmnTokenType.INT_LITERAL,
            LmnTokenType.LONG_LITERAL,
            LmnTokenType.FLOAT_LITERAL,
            LmnTokenType.DOUBLE_LITERAL
        ):
            val = token.value
            logger.debug(f"PrimaryParser: JSON numeric value => {val}")
            self.parser.advance()
            return val
        if ttype == LmnTokenType.TRUE:
            logger.debug("PrimaryParser: JSON boolean value => true")
            self.parser.advance()
            return True
        if ttype == LmnTokenType.FALSE:
            logger.debug("PrimaryParser: JSON boolean value => false")
            self.parser.advance()
            return False
        if ttype == LmnTokenType.NIL:
            logger.debug("PrimaryParser: JSON null => None")
            self.parser.advance()
            return None

        logger.error(f"PrimaryParser: Unexpected token in JSON value => {token}")
        raise SyntaxError(f"Unexpected token in JSON value: {token.value} ({ttype})")

    # -------------------------------------------------------------------------
    #  parse_array_literal => native array
    # -------------------------------------------------------------------------
    def parse_array_literal(self):
        """
        Parses a native array literal: [ expr1, expr2, ... ]
        Each element is a full expression, not just a JSON value.
        """
        logger.debug("PrimaryParser: Parsing native array literal.")
        self.parser.advance()  # consume '['
        elements = []

        if (
            self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.RBRACKET
        ):
            logger.debug("PrimaryParser: Detected empty native array ([]).")
            self.parser.advance()  # consume ']'
            return ArrayLiteralExpression(elements=elements)

        while True:
            expr = self.expr_parser.parse_expression()
            if expr is None:
                logger.error("PrimaryParser: Expected expression inside array literal.")
                raise SyntaxError("Expected expression inside array literal")
            elements.append(expr)
            logger.debug(f"PrimaryParser: Appended array element => {expr}")

            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                logger.debug("PrimaryParser: Detected ',' => continuing array parse.")
                self.parser.advance()  # consume ','
            else:
                self._expect(LmnTokenType.RBRACKET, "Expected ']' at end of array literal")
                self.parser.advance()  # consume ']'
                logger.debug("PrimaryParser: Completed native array parse.")
                break

        array_expr = ArrayLiteralExpression(elements=elements)
        logger.debug(f"PrimaryParser: Created ArrayLiteralExpression => {array_expr}")
        return array_expr

    # -------------------------------------------------------------------------
    #  _expect
    # -------------------------------------------------------------------------
    def _expect(self, token_type, message):
        if (
            not self.parser.current_token
            or self.parser.current_token.token_type != token_type
        ):
            logger.error(f"PrimaryParser: _expect failed => {message}")
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

        logger.debug("PrimaryParser: Checking bracket contents for '{' heuristic.")
        while pos < len(tokens):
            t = tokens[pos]
            if t.token_type == LmnTokenType.LBRACKET:
                depth += 1
            elif t.token_type == LmnTokenType.RBRACKET:
                depth -= 1
                if depth <= 0:
                    # Reached the matching ']'
                    logger.debug("PrimaryParser: Found matching ']' => ending bracket scan.")
                    break
            # If we see a '{' while bracket depth > 0, we suspect JSON
            elif t.token_type == LmnTokenType.LBRACE and depth > 0:
                logger.debug("PrimaryParser: Found '{' within bracket scope => JSON array likely.")
                return True

            pos += 1

        logger.debug("PrimaryParser: No '{' found within bracket scope => not JSON array.")
        return False
