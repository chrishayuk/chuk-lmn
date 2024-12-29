# file: tests/compiler/typechecker/statements/test_if_statement.py

import pytest
from pydantic import TypeAdapter

from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.statement_checker import check_statement

# Create a single TypeAdapter for your Node union
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
    # Create a symbol table: x => int
    symbol_table = {"x": "int"}

    check_statement(if_node, symbol_table)
    # If everything is correct, no exception is raised.
    assert if_node.inferred_type is None or if_node.inferred_type == "void"
    # (Depending on if your statement type checker sets if_node.inferred_type.)

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
    assert if_node.inferred_type is None or if_node.inferred_type == "void"

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
    symbol_table = {}

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

    # Should pass with no error, as all conditions are "int"
    check_statement(if_node, symbol_table)

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
                    "value": 3.14
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

    with pytest.raises(TypeError, match="ElseIf condition must be int/bool"):
        check_statement(if_node, symbol_table)
