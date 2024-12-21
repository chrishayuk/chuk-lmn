# tests/test_variable.py
import pytest
from compiler.ast.variable import Variable

def test_variable_basic():
    var = Variable("x")
    # Check string representation
    assert str(var) == "x"

    # Check to_dict
    result_dict = var.to_dict()
    assert result_dict["type"] == "Variable"
    assert result_dict["name"] == "x"

def test_variable_different_name():
    var = Variable("myVar")
    assert str(var) == "myVar"

    result_dict = var.to_dict()
    assert result_dict["type"] == "Variable"
    assert result_dict["name"] == "myVar"
