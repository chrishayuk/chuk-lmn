from typing import Optional, Dict
from lmn.compiler.ast import Expression
from lmn.compiler.typechecker.expressions.array_literal_checker import ArrayLiteralChecker
from lmn.compiler.typechecker.expressions.assignment_checker import AssignmentChecker
from lmn.compiler.typechecker.expressions.binary_checker import BinaryChecker
from lmn.compiler.typechecker.expressions.fn_checker import FnChecker
from lmn.compiler.typechecker.expressions.json_literal_checker import JsonLiteralChecker
from lmn.compiler.typechecker.expressions.literal_checker import LiteralChecker
from lmn.compiler.typechecker.expressions.postfix_checker import PostfixChecker
from lmn.compiler.typechecker.expressions.unary_checker import UnaryChecker
from lmn.compiler.typechecker.expressions.variable_checker import VariableChecker
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression

# Dispatcher to route expression checks to the appropriate class
class ExpressionDispatcher:
    def __init__(self, symbol_table: Dict[str, str]):
        # set the symbol table
        self.symbol_table = symbol_table

    def check_expression(self, expr: Expression, target_type: Optional[str] = None) -> str:
        if isinstance(expr, LiteralExpression):
            return LiteralChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, BinaryExpression):
            return BinaryChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, JsonLiteralExpression):
            return JsonLiteralChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, ArrayLiteralExpression):
            return ArrayLiteralChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, VariableExpression):
            return VariableChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, UnaryExpression):
            return UnaryChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, AssignmentExpression):
            return AssignmentChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, PostfixExpression):
            return PostfixChecker(self, self.symbol_table).check(expr, target_type)
        elif isinstance(expr, FnExpression):
            return FnChecker(self, self.symbol_table).check(expr, target_type)
        else:
            raise NotImplementedError(f"No checker available for {type(expr).__name__}.")

