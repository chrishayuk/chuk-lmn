# file: lmn/compiler/typechecker/literal_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import infer_literal_type

# -------------------------------------------------------------------------
# 3) LiteralExpression
# -------------------------------------------------------------------------

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

    def check(self, expr: LiteralExpression, target_type: Optional[str] = None) -> str:
        # check the type of a literal expression
        if expr.inferred_type is not None:
            # if the type is already inferred, return it
            return expr.inferred_type
        
        # check if the literal type is a known types
        if expr.literal_type in self.TYPE_MAPPING:
            # if the literal type is a known type, use it
            expr.inferred_type = self.TYPE_MAPPING[expr.literal_type]
        else:
            # otherwise, try to infer the type from the value
            expr.inferred_type = infer_literal_type(expr.value, target_type)

        # return the inferred type
        return expr.inferred_type
