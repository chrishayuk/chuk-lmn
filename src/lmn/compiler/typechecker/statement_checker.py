# file: lmn/compiler/typechecker/statement_checker.py
from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.statements.assignment_statement import check_assignment_statement
from lmn.compiler.typechecker.statements.set_statement import check_set_statement

def check_statement(stmt, symbol_table: dict) -> None:
    """
    A single statement could be SetStatement, PrintStatement, ReturnStatement, etc.
    We'll dispatch by stmt.type.
    """
    try:
        stype = stmt.type
        if stype == "SetStatement":
            # set statement
            check_set_statement(stmt, symbol_table)
        elif stype == "AssignmentStatement":
            # assignment statement
            check_assignment_statement(stmt, symbol_table)
        elif stype == "PrintStatement":
            # print statement
            check_print_statement(stmt, symbol_table)
        else:
            raise NotImplementedError(f"Unsupported statement type: {stype}")
    except TypeError as e:
        # Re-raise with context
        # Provide stype (the statement type) and, if present, stmt.variable_name
        # or fallback to something like 'unknown' if not available.
        raise TypeError(
            f"Error in {stype} "
            f"(variable={getattr(stmt, 'variable_name', getattr(stmt, 'name', 'unknown'))}): {e}"
        )


def check_print_statement(print_stmt, symbol_table: dict) -> None:
    """
    e.g. print_stmt.expressions is a list of Expression
    """
    for expr in print_stmt.expressions:
        e_type = check_expression(expr, symbol_table)
        # no further storage needed
