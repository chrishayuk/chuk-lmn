from typing import Optional, Dict
from lmn.compiler.ast import Expression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.typechecker.expressions.array_literal_checker import ArrayLiteralChecker
from lmn.compiler.typechecker.expressions.assignment_checker import AssignmentChecker
from lmn.compiler.typechecker.expressions.binary_checker import BinaryChecker
from lmn.compiler.typechecker.expressions.conversion_expression_checker import ConversionExpressionChecker
from lmn.compiler.typechecker.expressions.fn_checker import FnChecker
from lmn.compiler.typechecker.expressions.json_literal_checker import JsonLiteralChecker
from lmn.compiler.typechecker.expressions.literal_checker import LiteralChecker
from lmn.compiler.typechecker.expressions.postfix_checker import PostfixChecker
from lmn.compiler.typechecker.expressions.unary_checker import UnaryChecker
from lmn.compiler.typechecker.expressions.variable_checker import VariableChecker

# Suppose you add a new checker:
from lmn.compiler.typechecker.expressions.anonymous_function_checker import AnonymousFunctionChecker

# Import your various AST expression classes
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression

# If your anonymous function node is called AnonymousFunctionExpression:
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression

class ExpressionDispatcher:
    def __init__(self, symbol_table: Dict[str, str]):
        # Global or outer symbol table
        self.symbol_table = symbol_table

    def check_expression(
        self,
        expr: Expression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Dispatch the expression to the appropriate checker. 
        If local_scope is provided, pass it down to the checker 
        so variables/assignments are resolved in that scope.
        """
        if isinstance(expr, LiteralExpression):
            return LiteralChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, BinaryExpression):
            return BinaryChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, JsonLiteralExpression):
            return JsonLiteralChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, ArrayLiteralExpression):
            return ArrayLiteralChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, VariableExpression):
            return VariableChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, UnaryExpression):
            return UnaryChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, AssignmentExpression):
            return AssignmentChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, PostfixExpression):
            return PostfixChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, FnExpression):
            return FnChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, AnonymousFunctionExpression):
            return AnonymousFunctionChecker(self, self.symbol_table).check(expr, target_type, local_scope)
        elif isinstance(expr, ConversionExpression):
            return ConversionExpressionChecker(self, self.symbol_table).check(expr, target_type, local_scope)

        else:
            raise NotImplementedError(f"No checker available for {type(expr).__name__}.")
