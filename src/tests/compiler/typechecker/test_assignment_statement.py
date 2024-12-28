# tests/test_assignment_statement_typechecker.py

import pytest

from lmn.compiler.ast.statements.assignment_statement import AssignmentStatement
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression

from lmn.compiler.typechecker.statements.assignment_statement import check_assignment_statement
from lmn.compiler.typechecker.utils import unify_types

def test_assign_same_type_no_conversion():
    """
    If symbol_table has x -> 'i32',
    and we assign x = 42 (i32),
    there should be no type conflict or inserted conversion.
    """
    symbol_table = {"x": "i32"}
    stmt = AssignmentStatement(
        variable_name="x",
        expression=LiteralExpression(value=42, inferred_type="i32")
    )

    check_assignment_statement(stmt, symbol_table)
    
    assert stmt.inferred_type == "i32"
    # The expression should remain a LiteralExpression
    assert isinstance(stmt.expression, LiteralExpression)
    assert symbol_table["x"] == "i32"


def test_assign_promote_f32_to_f64():
    """
    If x is declared f64, but expression is an f32 literal, 
    we unify => final type f64, so we *might* insert a ConversionExpression.
    """
    symbol_table = {"x": "f64"}
    expr = LiteralExpression(value=2.718, inferred_type="f32")

    stmt = AssignmentStatement(
        variable_name="x",
        expression=expr
    )

    check_assignment_statement(stmt, symbol_table)

    # Final type is f64
    assert stmt.inferred_type == "f64"
    assert symbol_table["x"] == "f64"

    # If your code injects a ConversionExpression:
    if isinstance(stmt.expression, ConversionExpression):
        # Confirm the inserted conversion node
        conv = stmt.expression
        assert conv.from_type == "f32"
        assert conv.to_type == "f64"
        # Inside is the original literal
        assert isinstance(conv.source_expr, LiteralExpression)
        assert conv.source_expr.value == 2.718
    else:
        # Some language designs might skip explicit insertion
        pass


def test_assign_demote_f64_to_f32():
    """
    If x is declared f32, but expression is an f64 literal,
    we unify => final type f32. If your language allows demotion, 
    you might insert a ConversionExpression (f64 -> f32).
    
    If your language forbids demotion, you can uncomment the 'pytest.raises' 
    block and remove the lines after it, so the test expects a TypeError.
    """
    symbol_table = {"x": "f32"}
    expr = LiteralExpression(value=3.14159, inferred_type="f64")

    stmt = AssignmentStatement(
        variable_name="x",
        expression=expr
    )

    # If your language forbids demotion, do:
    # with pytest.raises(TypeError):
    #     check_assignment_statement(stmt, symbol_table)
    # return

    # Otherwise, let the checker allow it with an inserted conversion:
    check_assignment_statement(stmt, symbol_table)

    assert stmt.inferred_type == "f32"
    assert symbol_table["x"] == "f32"

    # Check if there's a ConversionExpression
    if isinstance(stmt.expression, ConversionExpression):
        conv = stmt.expression
        assert conv.from_type == "f64"
        assert conv.to_type == "f32"
        assert isinstance(conv.source_expr, LiteralExpression)
        assert conv.source_expr.value == 3.14159


def test_assign_unify_i32_to_i64():
    """
    If x is i64, but the expression is i32 => unify => i64 
    => possible i32->i64 extension.
    """
    symbol_table = {"x": "i64"}
    expr = LiteralExpression(value=42, inferred_type="i32")

    stmt = AssignmentStatement(
        variable_name="x",
        expression=expr
    )

    check_assignment_statement(stmt, symbol_table)
    assert stmt.inferred_type == "i64"
    assert symbol_table["x"] == "i64"

    # Possibly the expression is replaced with ConversionExpression(i32->i64)
    if isinstance(stmt.expression, ConversionExpression):
        conv = stmt.expression
        assert conv.from_type == "i32"
        assert conv.to_type == "i64"
        assert isinstance(conv.source_expr, LiteralExpression)


def test_assign_no_such_variable():
    """
    If symbol_table doesn't define 'y', we should fail with NameError.
    """
    symbol_table = {}
    stmt = AssignmentStatement(
        variable_name="y",
        expression=LiteralExpression(value=100, inferred_type="i32")
    )

    with pytest.raises(NameError):
        check_assignment_statement(stmt, symbol_table)
