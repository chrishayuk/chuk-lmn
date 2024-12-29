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

    # Optional: Verify the symbol_table now has 'doNothing' with return_type = None or 'void'
    # depending on your inference rules. For instance:
    # assert symbol_table["doNothing"]["return_type"] in (None, "void")

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

    # For example, you might check that "printHello" is now in the symbol_table
    # assert "printHello" in symbol_table

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
            {"name": "a", "type_annotation": "int"},
            {"name": "b", "type_annotation": "float"}
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

    # We expect check_function_definition to handle these typed params
    check_function_definition(func_def_node, symbol_table)

    # Optionally assert that the function is now in the symbol table with the correct param types
    # e.g. symbol_table["add"]["param_types"] = ["int", "float"] 
    # if your code normalizes "float" to "f32", adjust accordingly

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
            {"name": "y"}  # Omit 'type_annotation' entirely
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

    # This should succeed if your language allows untyped params (defaulting them to int, or None).
    check_function_definition(func_def_node, symbol_table)

    # e.g., the checker might store them as "int" or keep them as None.
    # assert "doStuff" in symbol_table
    # param_types = symbol_table["doStuff"]["param_types"]
    # assert param_types == ["int", "int"] or something else, depending on your language logic
