# file: tests/compiler/lowering/test_wasm_lowerer.py
import pytest
from typing import Dict, Any

# Suppose these are your actual imports:
from lmn.compiler.lowering.wasm_lowerer import lower_program_to_wasm_types
from lmn.compiler.ast.program import Program

def test_lower_simple_function_def():
    """
    Test that a FunctionDefinition node with 'return_type' == 'int'
    and param type 'long' is lowered to 'i32' and 'i64', respectively.
    """
    # A minimal AST in dictionary form
    ast_dict = {
        "type": "Program",
        "body": [
            {
                "type": "FunctionDefinition",
                "name": "sum",
                "params": [
                    {"type": "FunctionParameter", "name": "a", "type_annotation": "int"},
                    {"type": "FunctionParameter", "name": "b", "type_annotation": "long"}
                ],
                "body": [],
                "return_type": "int"
            }
        ]
    }

    # Validate/parse into Program node
    # (If you do program_node = Program(**ast_dict), or Program.model_validate(ast_dict))
    program_node = Program.model_validate(ast_dict)

    # Perform the lowering
    lower_program_to_wasm_types(program_node)

    # Check that everything was lowered properly
    assert program_node.body[0].return_type == "i32"

    # Check params
    assert program_node.body[0].params[0].type_annotation == "i32"  # was "int"
    assert program_node.body[0].params[1].type_annotation == "i64"  # was "long"


def test_lower_let_statement():
    """
    If a LetStatement has type_annotation='float' and expr.inferred_type='double',
    it should produce 'f32' and 'f64', etc.
    """
    ast_dict = {
        "type": "Program",
        "body": [
            {
                "type": "LetStatement",
                "variable": {
                    "type": "VariableExpression",
                    "name": "x",
                    "inferred_type": "double"
                },
                "type_annotation": "float", 
                "inferred_type": "float" 
            }
        ]
    }

    program_node = Program.model_validate(ast_dict)
    lower_program_to_wasm_types(program_node)

    let_stmt = program_node.body[0]
    # The LetStatement's type_annotation was "float" => now "f32"
    assert let_stmt.type_annotation == "f32"
    # The LetStatement itself might also have .inferred_type
    assert let_stmt.inferred_type == "f32"

    # The variable's inferred_type was "double" => now "f64"
    assert let_stmt.variable.inferred_type == "f64"


@pytest.mark.parametrize(
    "lang_type,expected",
    [
        ("int", "i32"),
        ("long", "i64"),
        ("float", "f32"),
        ("double", "f64"),
        ("someUnknownType", "i32"),  # if you default unknown => "i32"
    ]
)
def test_lower_individual_types(lang_type, expected):
    """
    A simple param test that uses a minimal Program with a single node
    to confirm the result of mapping from language to wasm types.
    """
    ast_dict = {
        "type": "Program",
        "body": [
            {
                "type": "LetStatement",
                "variable": {
                    "type": "VariableExpression",
                    "name": "testVar"
                },
                "type_annotation": lang_type, 
                "inferred_type": lang_type
            }
        ]
    }

    program_node = Program.model_validate(ast_dict)
    lower_program_to_wasm_types(program_node)

    let_stmt = program_node.body[0]
    assert let_stmt.type_annotation == expected
    assert let_stmt.inferred_type == expected


def test_lower_nested_binary_expression():
    """
    Example: A nested BinaryExpression with 'int' => 'i32'.
    """
    ast_dict = {
        "type": "Program",
        "body": [
            {
                "type": "AssignmentStatement",
                "variable_name": "z",
                "inferred_type": "int",
                "expression": {
                    "type": "BinaryExpression",
                    "operator": "+",
                    "inferred_type": "int",
                    "left": {
                        "type": "LiteralExpression",
                        "value": 5,
                        "inferred_type": "int"
                    },
                    "right": {
                        "type": "LiteralExpression",
                        "value": 10,
                        "inferred_type": "int"
                    }
                }
            }
        ]
    }

    program_node = Program.model_validate(ast_dict)
    lower_program_to_wasm_types(program_node)

    assign_stmt = program_node.body[0]
    # The assignment's inferred_type was "int" => now "i32"
    assert assign_stmt.inferred_type == "i32"

    bin_expr = assign_stmt.expression
    assert bin_expr.inferred_type == "i32"
    assert bin_expr.left.inferred_type == "i32"
    assert bin_expr.right.inferred_type == "i32"
