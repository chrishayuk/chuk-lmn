# file: tests/compiler/typechecker/statements/test_if_statement_typechecker.py

import pytest
from pydantic import TypeAdapter

from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.statement_checker import check_statement

# A single TypeAdapter for your Node union
node_adapter = TypeAdapter(Node)

def test_if_simple_no_else():
    """
    if (x < 10)
      print "Less"
    end
    - Condition is a BinaryExpression with operator "<"
    - 'x' is a variable => must be declared in symbol_table as int for no error
    - The literal 10 => int
    - The condition is int => that’s valid for an if condition in your language
    """
    dict_ast = {
        "type": "IfStatement",
        "condition": {
            "type": "BinaryExpression",
            "operator": "<",
            "left": {
                "type": "VariableExpression",
                "name": "x"
            },
            "right": {
                "type": "LiteralExpression",
                "value": 10  # defaults to "int"
            }
        },
        "then_body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "Less"
                    }
                ]
            }
        ],
        # no elseif_clauses
        # no else_body
    }

    if_node = node_adapter.validate_python(dict_ast)
    # Symbol table with x => int
    symbol_table = {"x": "int"}

    check_statement(if_node, symbol_table)
    # If everything is correct, no exception is raised.
    # By default, your typechecker might set if_node.inferred_type = "void" or leave it None.
    # So let's confirm it's either "void" or not present.
    assert getattr(if_node, "inferred_type", None) in (None, "void")


def test_if_with_else():
    """
    if (x >= 5)
      print "big"
    else
      print "small"
    end
    - Condition => x >= 5 => 'x' must be int, 5 => int
    - then_body => print "big"
    - else_body => print "small"
    """
    dict_ast = {
        "type": "IfStatement",
        "condition": {
            "type": "BinaryExpression",
            "operator": ">=",
            "left": {
                "type": "VariableExpression",
                "name": "x"
            },
            "right": {
                "type": "LiteralExpression",
                "value": 5
            }
        },
        "then_body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "big"
                    }
                ]
            }
        ],
        "else_body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "small"
                    }
                ]
            }
        ]
    }

    if_node = node_adapter.validate_python(dict_ast)
    symbol_table = {"x": "int"}

    check_statement(if_node, symbol_table)
    # same check for .inferred_type
    assert getattr(if_node, "inferred_type", None) in (None, "void")


def test_if_condition_not_int():
    """
    if "hello"
      print "Never do this"
    end
    - Condition is a string literal => your checker likely needs an int (or bool).
      => Should raise TypeError
    """
    dict_ast = {
        "type": "IfStatement",
        "condition": {
            "type": "LiteralExpression",
            "value": "hello"
        },
        "then_body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "Never do this"
                    }
                ]
            }
        ]
    }

    if_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}  # No definitions needed, though

    # Expect a TypeError because condition is "string" -> not in ("int", "bool")
    with pytest.raises(TypeError, match="If condition must be int/bool"):
        check_statement(if_node, symbol_table)


def test_if_with_elseif():
    """
    if (x > 10)
      print "Greater"
    elseif (x == 10)
      print "Equal"
    else
      print "Less"
    end
    - This tests an 'elseif_clauses' array
    """
    dict_ast = {
        "type": "IfStatement",
        "condition": {
            "type": "BinaryExpression",
            "operator": ">",
            "left": {
                "type": "VariableExpression",
                "name": "x"
            },
            "right": {
                "type": "LiteralExpression",
                "value": 10
            }
        },
        "then_body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "Greater"
                    }
                ]
            }
        ],
        "elseif_clauses": [
            {
                "type": "ElseIfClause",
                "condition": {
                    "type": "BinaryExpression",
                    "operator": "==",
                    "left": {
                        "type": "VariableExpression",
                        "name": "x"
                    },
                    "right": {
                        "type": "LiteralExpression",
                        "value": 10
                    }
                },
                "body": [
                    {
                        "type": "PrintStatement",
                        "expressions": [
                            {
                                "type": "LiteralExpression",
                                "value": "Equal"
                            }
                        ]
                    }
                ]
            }
        ],
        "else_body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "Less"
                    }
                ]
            }
        ]
    }

    if_node = node_adapter.validate_python(dict_ast)
    symbol_table = {"x": "int"}

    check_statement(if_node, symbol_table)
    assert getattr(if_node, "inferred_type", None) in (None, "void")


def test_if_with_elseif_condition_mismatch():
    """
    if (x > 10)
      print "Greater"
    elseif (3.14)   # invalid => condition is float/double, not 'int'
      print "Weird"
    end
    => TypeError
    """
    dict_ast = {
        "type": "IfStatement",
        "condition": {
            "type": "BinaryExpression",
            "operator": ">",
            "left": {
                "type": "VariableExpression",
                "name": "x"
            },
            "right": {
                "type": "LiteralExpression",
                "value": 10
            }
        },
        "then_body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "Greater"
                    }
                ]
            }
        ],
        "elseif_clauses": [
            {
                "type": "ElseIfClause",
                "condition": {
                    "type": "LiteralExpression",
                    "value": 3.14  # => "double"
                },
                "body": [
                    {
                        "type": "PrintStatement",
                        "expressions": [
                            {
                                "type": "LiteralExpression",
                                "value": "Weird"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    if_node = node_adapter.validate_python(dict_ast)
    symbol_table = {"x": "int"}

    # The condition for 'elseif' is "double", not "int"/"bool" => TypeError
    with pytest.raises(TypeError, match="ElseIf condition must be int/bool"):
        check_statement(if_node, symbol_table)
