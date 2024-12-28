# file: tests/emitter/wasm/statements/test_function_emitter.py

import pytest
from lmn.compiler.emitter.wasm.statements.function_emitter import FunctionEmitter

class DummyController:
    """
    A dummy controller for testing the FunctionEmitter.
    We'll stub out:
      - function_names: a list of known function names
      - func_local_map: a dict of { var_name: {type, index}, ... }
      - local_counter:  tracks the next local index
      - new_locals:     set of newly declared locals
      - emit_statement: method appending instructions to out_lines
    """
    def __init__(self):
        self.function_names = []
        self.func_local_map = {}
        self.local_counter = 0
        self.new_locals = set()

    def emit_statement(self, statement_node, out_lines):
        """
        Minimal stub for statements:
          { "op": "local.set", "args": ["x"] } => "  local.set $x"
          { "op": "local.get", "args": ["x"] } => "  local.get $x"
        If new variables appear in 'args', we add them to new_locals.
        """
        op = statement_node["op"]
        args = statement_node.get("args", [])

        # Register new locals if missing
        for arg in args:
            if arg not in self.func_local_map:
                self.new_locals.add(arg)

        arg_str = " ".join(f"${a}" for a in args)
        out_lines.append(f"  {op} {arg_str}")

@pytest.fixture
def controller():
    return DummyController()

@pytest.fixture
def function_emitter(controller):
    return FunctionEmitter(controller)

def test_no_params_no_body(function_emitter, controller):
    """
    Test a function with no params and an empty body
    """
    node = {
        "type": "FunctionDefinition",
        "name": "emptyFunc",
        "params": [],        # no parameters
        "body": []           # empty body
    }
    out_lines = []
    function_emitter.emit_function(node, out_lines)
    generated_wat = "\n".join(out_lines)

    # We expect something like:
    # (func $emptyFunc (result i32)
    #   i32.const 0
    #   return
    # )
    assert "(func $emptyFunc (result i32)" in generated_wat
    assert "i32.const 0" in generated_wat
    assert "return" in generated_wat
    assert generated_wat.strip().endswith(")")

def test_with_params_and_body(function_emitter, controller):
    """
    Test a function with parameters and a simple body.
    We'll push a param, do a local.set, then local.get, etc.
    """
    node = {
        "type": "FunctionDefinition",
        "name": "sumFirstN",
        "params": [
            { "type": "FunctionParameter", "name": "n" },
            { "type": "FunctionParameter", "name": "m" }
        ],
        "body": [
            { "op": "local.set", "args": ["temp"] },
            { "op": "local.get", "args": ["n"] },
            { "op": "local.get", "args": ["m"] }
        ]
    }
    out_lines = []
    function_emitter.emit_function(node, out_lines)
    generated_wat = "\n".join(out_lines)

    # Expected lines:
    # (func $sumFirstN (param $n i32) (param $m i32) (result i32)
    #   (local $temp i32)
    #   local.set $temp
    #   local.get $n
    #   local.get $m
    #   i32.const 0
    #   return
    # )
    assert "(func $sumFirstN (param $n i32) (param $m i32) (result i32)" in generated_wat
    # local declarations
    assert "(local $temp i32)" in generated_wat
    # instructions
    assert "local.set $temp" in generated_wat
    assert "local.get $n"   in generated_wat
    assert "local.get $m"   in generated_wat
    # fallback return
    assert "i32.const 0" in generated_wat
    assert generated_wat.strip().endswith(")")

def test_multiple_locals(function_emitter, controller):
    """
    Introduce multiple new locals via local.set statements: z, y, etc.
    Then local.get 'a' is a param. We'll confirm they're declared.
    """
    node = {
        "type": "FunctionDefinition",
        "name": "computeStuff",
        "params": [
            { "type": "FunctionParameter", "name": "a" }
        ],
        "body": [
            { "op": "local.set", "args": ["z"] },
            { "op": "local.set", "args": ["y"] },
            { "op": "local.get", "args": ["a"] },
            { "op": "local.get", "args": ["z"] }
        ]
    }
    out_lines = []
    function_emitter.emit_function(node, out_lines)
    generated_wat = "\n".join(out_lines)

    # We expect (local $y i32), (local $z i32), plus param a => (param $a i32)
    assert "(func $computeStuff (param $a i32) (result i32)" in generated_wat

    # local decl lines
    assert "(local $y i32)" in generated_wat
    assert "(local $z i32)" in generated_wat

    assert "local.set $z" in generated_wat
    assert "local.set $y" in generated_wat
    assert "local.get $a" in generated_wat
    assert "local.get $z" in generated_wat

    # fallback return
    assert "i32.const 0" in generated_wat
    assert generated_wat.strip().endswith(")")

def test_controller_updates(controller):
    """
    Confirm that function_names, func_local_map, etc. get updated as expected
    after multiple function definitions. We'll define two separate function nodes.
    """
    function_nodes = [
      {
        "type": "FunctionDefinition",
        "name": "funcA",
        "params": [
            { "type": "FunctionParameter", "name": "p1" }
        ],
        "body": []
      },
      {
        "type": "FunctionDefinition",
        "name": "funcB",
        "params": [],
        "body": []
      },
    ]
    emitter = FunctionEmitter(controller)

    out = []
    for fn_node in function_nodes:
        emitter.emit_function(fn_node, out)

    # Check we have 2 function names in controller
    assert "funcA" in controller.function_names
    assert "funcB" in controller.function_names

    joined_wat = "\n".join(out)
    # We expect each function in the WAT
    assert "(func $funcA (param $p1 i32) (result i32)" in joined_wat
    assert "(func $funcB (result i32)" in joined_wat

    # func_local_map typically resets per function, so after final function, 
    # it's param-only or empty
    assert isinstance(controller.func_local_map, dict)
    # no further checks if your code doesn't store param info in func_local_map
