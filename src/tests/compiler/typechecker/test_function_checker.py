# file: tests/compiler/typechecker/test_function_checker.py
from pydantic import TypeAdapter

# The union that includes FunctionDefinition
from lmn.compiler.ast.mega_union import Node

# Match the name in `function_checker.py`
from lmn.compiler.typechecker.function_checker import check_function_definition

# Create a single TypeAdapter for the `Node` union
node_adapter = TypeAdapter(Node)

def test_function_definition_basic():
    """
    Test that a function with no statements doesn't raise errors.
    """
    dict_func_def = {
        "type": "FunctionDefinition",
        "name": "doNothing",
        "params": [],
        "body": []  # No statements
    }
    func_def_node = node_adapter.validate_python(dict_func_def)
    symbol_table = {}

    # This should run without error
    check_function_definition(func_def_node, symbol_table)


def test_function_definition_with_statement():
    """
    Test a function that has one statement in its body.
    """
    dict_func_def = {
        "type": "FunctionDefinition",
        "name": "printHello",
        "params": [],
        "body": [
            {
                "type": "PrintStatement",
                "value": {
                    "type": "LiteralExpression",
                    "value": "Hello World"
                }
            }
        ]
    }
    func_def_node = node_adapter.validate_python(dict_func_def)
    symbol_table = {}

    # Again, should succeed if statement_checker handles PrintStatement
    check_function_definition(func_def_node, symbol_table)
