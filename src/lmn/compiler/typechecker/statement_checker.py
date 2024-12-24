# file: lmn/compiler/typechecker/statement_checker.py
from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.utils import unify_types

def check_statement(stmt, symbol_table: dict) -> None:
    """
    A single statement could be SetStatement, PrintStatement, ReturnStatement, etc.
    We'll dispatch by stmt.type.
    """
    stype = stmt.type
    if stype == "SetStatement":
        check_set_statement(stmt, symbol_table)
    elif stype == "PrintStatement":
        check_print_statement(stmt, symbol_table)
    else:
        raise NotImplementedError(f"Unsupported statement type: {stype}")


def check_set_statement(set_stmt, symbol_table: dict) -> None:
    """
    e.g. set_stmt.variable is a VariableExpression, set_stmt.expression is an Expression
    """
    expr_type = check_expression(set_stmt.expression, symbol_table)

    var_expr = set_stmt.variable
    if var_expr.type != "VariableExpression":
        raise TypeError("Left-hand side of set must be a VariableExpression")

    var_name = var_expr.name
    if var_name not in symbol_table:
        symbol_table[var_name] = expr_type
    else:
        existing_type = symbol_table[var_name]
        new_type = unify_types(existing_type, expr_type)
        symbol_table[var_name] = new_type

    # Optionally store an inferred_type on the node
    set_stmt.inferred_type = expr_type


def check_print_statement(print_stmt, symbol_table: dict) -> None:
    """
    e.g. print_stmt.expressions is a list of Expression
    """
    for expr in print_stmt.expressions:
        e_type = check_expression(expr, symbol_table)
        # no further storage needed
