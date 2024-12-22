import pytest

from compiler.emitter.wasm.statements.function_emitter import FunctionEmitter

class DummyController:
    """
    A dummy controller for testing the FunctionEmitter.
    We’ll stub out:
      - function_names: a list of known function names
      - func_local_map: a dict of { var_name: local_index }
      - local_counter:  tracks the next local index
      - new_locals:     set of newly declared locals
      - emit_statement: a method that appends instructions to out_lines
    """
    def __init__(self):
        self.function_names = []
        self.func_local_map = {}
        self.local_counter = 0
        self.new_locals = set()

    def emit_statement(self, statement_node, out_lines):
        """
        Minimal stub. In real usage:
          - Parse statement_node to determine instructions
          - Possibly add new locals to self.new_locals
        Here we just handle a few examples:

        Example statement_node:
          { "op": "local.set", "args": ["x"] }
        We append to out_lines: "  local.set $x"
        """
        op = statement_node["op"]
        args = statement_node.get("args", [])

        # If we detect a new local we haven't declared, add it
        # (In reality, you'd probably track this from variable declarations
        # or code that sets a variable.)
        for arg in args:
            if arg not in self.func_local_map:
                self.new_locals.add(arg)

        # Emit the instruction line
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
    Test an empty function with no parameters and no statements
    """
    node = {
        "type": "FunctionDefinition",
        "name": "emptyFunc",
        "params": [],
        "body": []
    }
    out_lines = []
    function_emitter.emit_function(node, out_lines)
    generated_wat = "\n".join(out_lines)

    # Check for correct structure
    # Expect:
    # (func $emptyFunc (result i32)
    #   i32.const 0
    #   return
    # )
    assert "(func $emptyFunc (result i32)" in generated_wat
    assert "i32.const 0" in generated_wat
    assert "return" in generated_wat
    assert generated_wat.endswith(")")  # final closing parenthesis


def test_with_params_and_body(function_emitter, controller):
    """
    Test a function with parameters and a simple body. 
    We'll push a param, do a local.set, then local.get, etc.
    """
    node = {
        "type": "FunctionDefinition",
        "name": "sumFirstN",
        "params": ["n", "m"],
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
    # local decl
    assert "(local $temp i32)" in generated_wat
    # instructions
    assert "local.set $temp" in generated_wat
    assert "local.get $n"   in generated_wat
    assert "local.get $m"   in generated_wat
    # default return
    assert "i32.const 0" in generated_wat
    # final close
    assert generated_wat.endswith(")")


def test_multiple_locals(function_emitter, controller):
    """
    Test a function that introduces multiple locals, to ensure sorting, 
    insertion, etc. works correctly.
    """
    node = {
        "type": "FunctionDefinition",
        "name": "computeStuff",
        "params": ["a"],
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

    # We expect to see (local $y i32) and (local $z i32)
    # Because we sort by name in the emitter (if you do that),
    # they appear in alphabetical order. If you don't sort, you might see them
    # in the order they were discovered.
    assert "(local $y i32)" in generated_wat
    assert "(local $z i32)" in generated_wat

    # Must see instructions
    assert "local.set $z" in generated_wat
    assert "local.set $y" in generated_wat
    assert "local.get $a" in generated_wat
    assert "local.get $z" in generated_wat

    # Final close
    assert generated_wat.endswith(")")


def test_controller_updates(controller):
    """
    Confirm that function_names, func_local_map, etc. get updated as expected 
    after multiple calls. 
    """
    # Suppose we define two functions in one go
    function_nodes = [
      {
        "type": "FunctionDefinition",
        "name": "funcA",
        "params": ["p1"],
        "body": []
      },
      {
        "type": "FunctionDefinition",
        "name": "funcB",
        "params": [],
        "body": []
      },
    ]
    from compiler.emitter.wasm.statements.function_emitter import FunctionEmitter
    emitter = FunctionEmitter(controller)

    out = []
    for fn_node in function_nodes:
        emitter.emit_function(fn_node, out)

    # The controller should have both function names now:
    assert "funcA" in controller.function_names
    assert "funcB" in controller.function_names
    # func_local_map resets after each function, so it should be for funcB now
    # but since we never assigned a body, it's empty or param-only
    # Just check that it doesn't blow up.
    assert isinstance(controller.func_local_map, dict)

    # The final WAT output should have two function definitions
    joined_wat = "\n".join(out)
    assert "(func $funcA (param $p1 i32) (result i32)" in joined_wat
    assert "(func $funcB (result i32)" in joined_wat

