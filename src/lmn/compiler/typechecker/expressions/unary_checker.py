# file: lmn/compiler/typechecker/unary_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

class UnaryChecker(BaseExpressionChecker):
    def check(
        self,
        expr: UnaryExpression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Type-check a UnaryExpression (e.g. -x, +x, not x).

        :param expr: The UnaryExpression AST node.
        :param target_type: An optional hinted type.
        :param local_scope: A local scope dict if available, otherwise self.symbol_table is used.
        :return: The inferred or unified type of the unary expression.
        """
        # Decide which scope to use for lookups
        scope = local_scope if local_scope is not None else self.symbol_table

        # 1) Check the type of the operand (passing local_scope)
        operand_type = self.dispatcher.check_expression(expr.operand, local_scope=scope)

        # 2) Get the operator
        op = expr.operator

        # 3) Check if the operand is compatible with the operator
        if op in ("+", "-"):
            # numeric operators
            if operand_type not in ("int", "long", "float", "double"):
                raise TypeError(
                    f"Cannot apply unary '{op}' to '{operand_type}'. Must be numeric."
                )
            result_type = operand_type

        elif op == "not":
            # boolean operator (in LMN, 'int' is used for booleans)
            if operand_type != "int":
                raise TypeError(
                    f"Cannot apply 'not' to '{operand_type}'. Expecting 'int' as boolean."
                )
            result_type = "int"

        else:
            # unknown/unimplemented operator
            raise NotImplementedError(f"Unknown unary operator '{op}'")

        # 4) Set the inferred type of the expression
        expr.inferred_type = result_type

        # 5) Return the type of the expression
        return result_type
