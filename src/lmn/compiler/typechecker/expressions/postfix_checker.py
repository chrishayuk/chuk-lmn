# file: lmn/compiler/typechecker/postfix_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
class PostfixChecker(BaseExpressionChecker):
    def check(
        self,
        expr: PostfixExpression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Type-check a PostfixExpression (e.g. x++ or x--).

        :param expr: The PostfixExpression AST node.
        :param target_type: Optional type hint.
        :param local_scope: A local scope dict if available, otherwise self.symbol_table is used.
        :return: The inferred type (same as operand's type).
        """

        # 1) Determine the operand's type, passing local_scope for variable lookups
        operand_type = self.dispatcher.check_expression(expr.operand, local_scope=local_scope)

        # 2) Check the operator (e.g. '++' or '--')
        operator = expr.operator

        # 3) Validate that operand_type is numeric
        if operand_type not in ("int", "long", "float", "double"):
            raise TypeError(f"Cannot apply postfix '{operator}' to '{operand_type}'. Must be numeric.")

        # 4) The resulting type is the same as the operand's type
        expr.inferred_type = operand_type

        # 5) Return the inferred type
        return operand_type
