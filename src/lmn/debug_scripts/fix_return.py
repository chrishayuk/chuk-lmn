# fix_return.py
from lmn.compiler.ast.statements.return_statement import ReturnStatement
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression

def main():
    ret_stmt = ReturnStatement()
    print("ReturnStatement in memory =>", ret_stmt)
    print("ReturnStatement as dict =>", ret_stmt.to_dict())

    func_expr = AnonymousFunctionExpression(
        parameters=[("a", None), ("b", None)],
        body=[ret_stmt]
    )
    print("\nAnonymousFunctionExpression in memory =>", func_expr)
    print("AnonymousFunctionExpression as dict =>", func_expr.to_dict())

if __name__ == "__main__":
    main()
