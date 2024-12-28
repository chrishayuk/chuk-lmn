# file: tests/compiler/typechecker/test_function_checker.py

from pydantic import TypeAdapter

# The union that includes FunctionDefinition
from lmn.compiler.ast.mega_union import Node

# The checker we want to test
from lmn.compiler.typechecker.function_checker import check_function_definition

# Create a single TypeAdapter for the `Node` union
node_adapter = TypeAdapter(Node)


def test_function_definition_basic():
    """
    A function with no statements and no params shouldn't raise errors.
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
    A function that has one PrintStatement in its body.
    """
    dict_func_def = {
        "type": "FunctionDefinition",
        "name": "printHello",
        "params": [],
        "body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {
                        "type": "LiteralExpression",
                        "value": "Hello World"
                    }
                ]
            }
        ]
    }
    func_def_node = node_adapter.validate_python(dict_func_def)
    symbol_table = {}

    # Should succeed if statement_checker handles PrintStatement
    check_function_definition(func_def_node, symbol_table)


def test_function_with_typed_params():
    """
    function add(a: int, b: float)
      print a b
    end
    """
    dict_func_def = {
        "type": "FunctionDefinition",
        "name": "add",
        "params": [
            {"name": "a", "type_annotation": "int"},   # => i32
            {"name": "b", "type_annotation": "float"}  # => f32
        ],
        "body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {"type": "VariableExpression", "name": "a"},
                    {"type": "VariableExpression", "name": "b"}
                ]
            }
        ]
    }
    func_def_node = node_adapter.validate_python(dict_func_def)
    symbol_table = {}

    # We expect check_function_definition to put 'a' => i32, 'b' => f32 in the local table
    check_function_definition(func_def_node, symbol_table)

    # If your checker merges function params into the top-level table, 
    # you might test for symbol_table["a"] == "i32" etc.
    # Or if they remain function-local, you won't see them in the global table.


def test_function_with_untyped_params():
    """
    function doStuff(x, y)
      print x y
    end
    """
    dict_func_def = {
        "type": "FunctionDefinition",
        "name": "doStuff",
        "params": [
            {"name": "x", "type_annotation": None},
            {"name": "y"}  # Or omit 'type_annotation' field
        ],
        "body": [
            {
                "type": "PrintStatement",
                "expressions": [
                    {"type": "VariableExpression", "name": "x"},
                    {"type": "VariableExpression", "name": "y"}
                ]
            }
        ]
    }
    func_def_node = node_adapter.validate_python(dict_func_def)
    symbol_table = {}

    # The checker might set x => None, y => None in the local table,
    # or let them be inferred as usage continues.
    check_function_definition(func_def_node, symbol_table)
    # No error expected for untyped parameters if your language allows them.
