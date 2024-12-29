# file: tests/compiler/typechecker/statements/test_block_scope.py

import pytest
from pydantic import TypeAdapter

from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.statement_checker import check_statement

# Create a single TypeAdapter for your Node union
node_adapter = TypeAdapter(Node)

def test_block_scope_variable_not_visible_outside():
    """
    A nested block declares 'y'. Attempting to print 'y' outside that block 
    should raise a type error (because 'y' is out of scope).
    
    Example pseudo-code:
        begin
            let x = 10

            begin
                let y = 5
                print y  # OK, y is in scope
            end

            print y      # ERROR: y not in scope here
        end
    """

    dict_ast = {
        "type": "BlockStatement",
        "statements": [
            # let x = 10
            {
                "type": "LetStatement",
                "variable": {
                    "type": "VariableExpression",
                    "name": "x"
                },
                "expression": {
                    "type": "LiteralExpression",
                    "value": 10
                }
            },
            # begin
            {
                "type": "BlockStatement",
                "statements": [
                    # let y = 5
                    {
                        "type": "LetStatement",
                        "variable": {
                            "type": "VariableExpression",
                            "name": "y"
                        },
                        "expression": {
                            "type": "LiteralExpression",
                            "value": 5
                        }
                    },
                    # print y
                    {
                        "type": "PrintStatement",
                        "expressions": [
                            {
                                "type": "VariableExpression",
                                "name": "y"
                            }
                        ]
                    }
                ]
            },
            # print y (ERROR!)
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "VariableExpression",
                        "name": "y"
                    }
                ]
            }
        ]
    }

    block_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    # Because 'y' is declared only in the inner block, printing it outside 
    # should raise a TypeError (or whatever error your checker raises). 
    with pytest.raises(TypeError, match="Variable 'y' used before assignment"):
        check_statement(block_node, symbol_table)


def test_block_scope_shadowing():
    """
    Tests that an inner block can 'shadow' a variable declared in the outer block.

    Example pseudo-code:
        begin
            let x = 1
            begin
                let x = 2
                print x  # prints 2 (inner x)
            end
            print x      # prints 1 (outer x)
        end

    This should NOT raise an error; both prints refer to valid variables.
    """

    dict_ast = {
        "type": "BlockStatement",
        "statements": [
            # let x = 1
            {
                "type": "LetStatement",
                "variable": {
                    "type": "VariableExpression",
                    "name": "x"
                },
                "expression": {
                    "type": "LiteralExpression",
                    "value": 1
                }
            },
            # inner block
            {
                "type": "BlockStatement",
                "statements": [
                    # let x = 2
                    {
                        "type": "LetStatement",
                        "variable": {
                            "type": "VariableExpression",
                            "name": "x"
                        },
                        "expression": {
                            "type": "LiteralExpression",
                            "value": 2
                        }
                    },
                    # print x (inner)
                    {
                        "type": "PrintStatement",
                        "expressions": [
                            {
                                "type": "VariableExpression",
                                "name": "x"
                            }
                        ]
                    }
                ]
            },
            # print x (outer)
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "VariableExpression",
                        "name": "x"
                    }
                ]
            }
        ]
    }

    block_node = node_adapter.validate_python(dict_ast)
    symbol_table = {}

    # This should NOT raise an error:
    check_statement(block_node, symbol_table)
