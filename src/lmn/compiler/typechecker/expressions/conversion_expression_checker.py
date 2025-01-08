# file: lmn/compiler/typechecker/expressions/conversion_expression_checker.py
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

class ConversionExpressionChecker(BaseExpressionChecker):
    def check(self, expr, target_type=None, local_scope=None) -> str:
        """
        Handles a ConversionExpression node, e.g. from_type='void', to_type='int', etc.
        Usually we'll type-check the source_expr, unify with 'from_type', and produce 'to_type'.
        """
        # 1) Type-check source_expr
        source_expr = expr.source_expr
        source_type = self.dispatcher.check_expression(source_expr, target_type=None, local_scope=local_scope)

        # 2) If you want, unify source_type with expr.from_type (though it's optional
        #    if from_type is an artifact from earlier passes).
        unify_types(expr.from_type, source_type, for_assignment=False) # optional

        # 3) The final type is expr.to_type
        expr.inferred_type = expr.to_type

        # return the inferred type
        return expr.inferred_type
