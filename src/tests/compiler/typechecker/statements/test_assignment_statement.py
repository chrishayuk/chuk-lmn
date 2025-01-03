# file: tests/compiler/typechecker/statements/test_assignment_statement_typechecker.py

import pytest

# AST Nodes for the statement and various expressions
from lmn.compiler.ast.statements.assignment_statement import AssignmentStatement
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression

# The checker under test
from lmn.compiler.typechecker.statements.assignment_statement_checker import check_assignment_statement
from lmn.compiler.typechecker.utils import unify_types


def test_assign_same_type_no_conversion():
    """
    If symbol_table has x -> 'int',
    and we assign x = 42 (int),
    there should be no type conflict or inserted conversion.
    """
    symbol_table = {"x": "int"}
    stmt = AssignmentStatement(
        variable_name="x",
        expression=LiteralExpression(value=42, inferred_type="int")
    )

    check_assignment_statement(stmt, symbol_table)
    
    assert stmt.inferred_type == "int"
    # The expression remains a LiteralExpression (no conversion needed).
    assert isinstance(stmt.expression, LiteralExpression)
    assert symbol_table["x"] == "int"


def test_assign_promote_float_to_double():
    """
    If x is declared 'double', but expression is a 'float' literal,
    we unify => final type 'double'. 
    If your language inserts a ConversionExpression for the promotion,
    verify that here.
    """
    symbol_table = {"x": "double"}
    expr = LiteralExpression(value=2.718, inferred_type="float")

    stmt = AssignmentStatement(
        variable_name="x",
        expression=expr
    )

    check_assignment_statement(stmt, symbol_table)

    # Final type is 'double'
    assert stmt.inferred_type == "double"
    assert symbol_table["x"] == "double"

    # If your typechecker inserts a ConversionExpression:
    if isinstance(stmt.expression, ConversionExpression):
        conv = stmt.expression
        assert conv.from_type == "float"
        assert conv.to_type == "double"
        # The inside should be the original literal
        assert isinstance(conv.source_expr, LiteralExpression)
        assert conv.source_expr.value == 2.718
    else:
        # Some languages might skip explicit node insertion.
        pass


def test_assign_demote_double_to_float():
    """
    If x is declared 'float', but expression is a 'double' literal,
    we unify => final type 'float'. If your language allows demotion, 
    you might insert a ConversionExpression (double -> float).

    If your language forbids demotion, you can:
      1) raise a TypeError, OR
      2) require an explicit cast in the code.
    """
    symbol_table = {"x": "float"}
    expr = LiteralExpression(value=3.14159, inferred_type="double")

    stmt = AssignmentStatement(
        variable_name="x",
        expression=expr
    )

    # If your language forbids demotion, do:
    # with pytest.raises(TypeError):
    #     check_assignment_statement(stmt, symbol_table)
    # return

    # Otherwise, let the checker allow it:
    check_assignment_statement(stmt, symbol_table)

    assert stmt.inferred_type == "float"
    assert symbol_table["x"] == "float"

    # Check if there's a ConversionExpression
    if isinstance(stmt.expression, ConversionExpression):
        conv = stmt.expression
        assert conv.from_type == "double"
        assert conv.to_type == "float"
        assert isinstance(conv.source_expr, LiteralExpression)
        assert conv.source_expr.value == 3.14159


def test_assign_unify_int_to_long():
    """
    If x is 'long', but the expression is 'int', unify => 'long'
    => possible extension from int to long.
    """
    symbol_table = {"x": "long"}
    expr = LiteralExpression(value=42, inferred_type="int")

    stmt = AssignmentStatement(
        variable_name="x",
        expression=expr
    )

    check_assignment_statement(stmt, symbol_table)
    assert stmt.inferred_type == "long"
    assert symbol_table["x"] == "long"

    # Possibly the expression is replaced with a ConversionExpression(int->long)
    if isinstance(stmt.expression, ConversionExpression):
        conv = stmt.expression
        assert conv.from_type == "int"
        assert conv.to_type == "long"
        assert isinstance(conv.source_expr, LiteralExpression)


def test_assign_no_such_variable():
    """
    If symbol_table doesn't define 'y', 
    we should fail with NameError.
    """
    symbol_table = {}
    stmt = AssignmentStatement(
        variable_name="y",
        expression=LiteralExpression(value=100, inferred_type="int")
    )

    with pytest.raises(NameError):
        check_assignment_statement(stmt, symbol_table)
