# tests/emitter/wasm/statements/test_function_emitter.py
import pytest
from compiler.emitter.wasm.statements.function_emitter import FunctionEmitter

class MockController:
    def __init__(self):
        # For exporting or referencing
        self.function_names = []

        # Local info
        self.func_local_map = {}
        self.local_counter = 0
        self.new_locals = set()

    def emit_statement(self, stmt, out_lines):
        # For testing, let's say we see a "SetStatement" that declares a new variable "x"
        # In real usage, you'd parse stmt["type"] => call the correct emitter.
        if stmt["type"] == "SetStatement":
            var_name = stmt["variable"]["name"]
            # if new
            if var_name not in self.func_local_map:
                self.func_local_map[var_name] = self.local_counter
                self.local_counter += 1
                self.new_locals.add(var_name)
            # simulate instructions
            out_lines.append(f'  i32.const {stmt["expression"]["value"]}')
            out_lines.append(f'  local.set ${var_name}')
        else:
            # placeholder for other statement types
            out_lines.append('  ;; some statement')

def test_function_no_params():
    """
    Simple function with no params, one set statement that declares 'x'.
    We'll see:
      (func $myFunc (result i32)
        (local $x i32)
        i32.const 42
        local.set $x
        i32.const 0
        return
      )
    """
    emitter = FunctionEmitter(MockController())

    node = {
        "type": "FunctionDefinition",
        "name": "myFunc",
        "params": [],
        "body": [
            {
                "type": "SetStatement",
                "variable": {"type": "VariableExpression", "name": "x"},
                "expression": {"type": "LiteralExpression", "value": 42}
            }
        ]
    }

    out_lines = []
    emitter.emit_function(node, out_lines)
    combined = "\n".join(out_lines)

    # Check for function header
    assert "(func $myFunc (result i32" in combined

    # We expect to see "(local $x i32)" AFTER the (func ...) line
    # Then "i32.const 42" and "local.set $x"
    assert "(local $x i32)" in combined
    assert "i32.const 42" in combined
    assert "local.set $x" in combined

    # We expect the fallback "i32.const 0" + "return"
    assert "i32.const 0" in combined
    assert "return" in combined

    # And it ends with a ")"
    assert combined.endswith(")")

def test_function_with_params():
    """
    A function with parameters => should have (param $n i32) etc.
    Also check that if no new locals appear, we don't see any (local ...)
    statements.
    """
    emitter = FunctionEmitter(MockController())

    node = {
        "type": "FunctionDefinition",
        "name": "adder",
        "params": ["n", "m"],
        "body": [
            # no new local, just some placeholder
            { "type": "OtherStatement" }
        ]
    }

    out_lines = []
    emitter.emit_function(node, out_lines)
    combined = "\n".join(out_lines)

    # Check we have (func $adder (param $n i32) (param $m i32) (result i32)
    assert "(func $adder (param $n i32) (param $m i32) (result i32)" in combined

    # We have no new local => no (local $...) line
    assert "(local $n i32)" not in combined
    assert "(local $m i32)" not in combined

    # We DO see i32.const 0 and return
    assert "i32.const 0" in combined
    assert "return" in combined

    # Ends with ')'
    assert combined.endswith(")")
