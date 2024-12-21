# debug_fields.py
from compiler.ast.expressions.literal_expression import LiteralExpression
from compiler.ast.expressions.variable_expression import VariableExpression
from compiler.ast.expressions.binary_expression import BinaryExpression
from compiler.ast.expressions.unary_expression import UnaryExpression
from compiler.ast.expressions.fn_expression import FnExpression

# 1) Test: test_literal_int
print("==== Debugging test_literal_int ====")
lit_int = LiteralExpression(value="5")
print("to_dict() =>", lit_int.to_dict())
print("model_dump() =>", lit_int.model_dump())
print()

# 2) Test: test_literal_float
print("==== Debugging test_literal_float ====")
lit_float = LiteralExpression(value="3.14")
print("to_dict() =>", lit_float.to_dict())
print("model_dump() =>", lit_float.model_dump())
print()

# 3) Test: test_literal_string
print("==== Debugging test_literal_string ====")
lit_string = LiteralExpression(value="hello")
print("to_dict() =>", lit_string.to_dict())
print("model_dump() =>", lit_string.model_dump())
print()

# 4) Test: test_binary_expression
print("==== Debugging test_binary_expression ====")
left = LiteralExpression(value="5")
right = LiteralExpression(value="3")
bin_expr = BinaryExpression(operator="+", left=left, right=right)
print("to_dict() =>", bin_expr.to_dict())
print("model_dump() =>", bin_expr.model_dump())
print()

# 5) Test: test_unary_expression
print("==== Debugging test_unary_expression ====")
operand = LiteralExpression(value="10")
un_expr = UnaryExpression(operator="-", operand=operand)
print("to_dict() =>", un_expr.to_dict())
print("model_dump() =>", un_expr.model_dump())
print()

# 6) Test: test_fn_expression_single_arg
print("==== Debugging test_fn_expression_single_arg ====")
name = VariableExpression(name="fact")
arg = LiteralExpression(value="5")
fn_expr_single = FnExpression(name=name, arguments=[arg])
print("to_dict() =>", fn_expr_single.to_dict())
print("model_dump() =>", fn_expr_single.model_dump())
print()

# 7) Test: test_fn_expression_multiple_args
print("==== Debugging test_fn_expression_multiple_args ====")
name_mult = VariableExpression(name="sum")
arg1 = VariableExpression(name="a")
arg2 = VariableExpression(name="b")
arg3 = LiteralExpression(value="10")
fn_expr_multiple = FnExpression(name=name_mult, arguments=[arg1, arg2, arg3])
print("to_dict() =>", fn_expr_multiple.to_dict())
print("model_dump() =>", fn_expr_multiple.model_dump())
print()
