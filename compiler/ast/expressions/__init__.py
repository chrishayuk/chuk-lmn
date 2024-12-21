# compiler/ast/expressions/__init__.py
from .expression_kind import ExpressionKind
from .expression import Expression
from .literal_expression import LiteralExpression
from .variable_expression import VariableExpression
from .binary_expression import BinaryExpression
from .unary_expression import UnaryExpression
from .fn_expression import FnExpression
from .expression_union import ExpressionUnion  # contains the Annotated[Union[...], Field(discriminator=...)]

# Now that everything is imported, rebuild them so Pydantic sees fully defined references
LiteralExpression.model_rebuild()
VariableExpression.model_rebuild()
BinaryExpression.model_rebuild()
UnaryExpression.model_rebuild()
FnExpression.model_rebuild()
