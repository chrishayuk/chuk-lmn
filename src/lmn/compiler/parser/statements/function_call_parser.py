# file: lmn/compiler/parser/statements/function_call_parser.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression  # or create a separate CallStatement node

logger = logging.getLogger(__name__)

class FunctionCallParser:
    def __init__(self, parent_parser, func_name: str):
        """
        parent_parser: the main Parser
        func_name: the name of the function being called
        """
        self.parser = parent_parser
        self.func_name = func_name

    def parse(self):
        """
        Parses a function call statement of the form:
            funcName(expr1, expr2, ...)
        Returns either a FnExpression or a dedicated CallStatement AST node.
        """
        logger.debug("FnCallParser: Starting parse of function call => %r", self.func_name)

        # Expect '('
        expect_token(self.parser, LmnTokenType.LPAREN, f"Expected '(' after {self.func_name}")
        self.parser.advance()  # consume '('

        args = []
        # Parse zero or more arguments until we see ')'
        while True:
            current = self.parser.current_token
            if not current:
                raise SyntaxError("Unexpected end of input inside function call arguments")

            if current.token_type == LmnTokenType.RPAREN:
                # end of arg list
                break

            # parse an expression argument
            arg = self.parser.expression_parser.parse_expression()
            if arg is None:
                raise SyntaxError("Expected expression in function call arguments")

            args.append(arg)

            # If next token is ',', consume it and continue
            if (
                self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.COMMA
            ):
                self.parser.advance()  # consume ','
            else:
                # otherwise, we expect ')'
                break

        # Now expect ')'
        expect_token(self.parser, LmnTokenType.RPAREN, f"Expected ')' after arguments to {self.func_name}")
        self.parser.advance()  # consume ')'

        # Return a call AST node. For a statement, you might want a `CallStatement`.
        # For instance, you can do:
        from lmn.compiler.ast.statements.call_statement import CallStatement
        logger.debug("FnCallParser: Building CallStatement => %s(...)", self.func_name)

        # If you just want an expression, do FnExpression(...). For a statement, do:
        return CallStatement(
            tool_name=self.func_name,
            arguments=args
        )
