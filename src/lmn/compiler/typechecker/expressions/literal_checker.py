# file: lmn/compiler/typechecker/literal_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import infer_literal_type

class LiteralChecker(BaseExpressionChecker):
    # type maps
    TYPE_MAPPING = {
        "f32": "float",
        "float": "float",
        "f64": "double",
        "double": "double",
        "i32": "int",
        "int": "int",
        "i64": "long",
        "long": "long",
        "string": "string",
    }

    def check(
        self,
        expr: LiteralExpression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Type-check a LiteralExpression.

        :param expr: The literal expression node.
        :param target_type: An optional hint (e.g. if assigned to a variable of type 'int').
        :param local_scope: A local scope dictionary, if provided (unused here, but consistent with other checkers).
        :return: The inferred type of the literal expression (e.g. 'int', 'float', 'string', etc.).
        """
        # if the type is already inferred, return it
        if expr.inferred_type is not None:
            return expr.inferred_type
        
        # check if the literal type is one of the known types in TYPE_MAPPING
        if expr.literal_type in self.TYPE_MAPPING:
            expr.inferred_type = self.TYPE_MAPPING[expr.literal_type]
        else:
            # otherwise, try to infer the type from the value
            expr.inferred_type = infer_literal_type(expr.value, target_type)

        return expr.inferred_type
