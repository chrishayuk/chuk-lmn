# file: lmn/compiler/ast/expressions/conversion_expression.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal
from pydantic import BaseModel

if TYPE_CHECKING:
    from lmn.compiler.ast.mega_union import Expression

class ConversionExpression(BaseModel):
    """
    Represents an explicit numeric conversion from one type to another,
    e.g. f64->f32 demotion, f32->f64 promotion, i32->i64 extension, etc.
    """
    type: Literal["ConversionExpression"] = "ConversionExpression"

    from_type: str
    to_type: str

    # We'll store the expression being converted, referencing 'Expression' as a forward ref
    source_expr: "Expression"

    # If you store an inferred type
    inferred_type: Optional[str] = None

    def __str__(self):
        return (f"ConversionExpression({self.from_type}->{self.to_type}, "
                f"source_expr={self.source_expr})")
