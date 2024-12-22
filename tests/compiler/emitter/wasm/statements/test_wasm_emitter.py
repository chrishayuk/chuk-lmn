# tests/emitter/wasm/test_wasm_emitter.py
import pytest
from compiler.emitter.wasm.wasm_emitter import WasmEmitter

def test_emit_program_with_function():
    ast = {
      "type": "Program",
      "body": [
        {
          "type": "FunctionDefinition",
          "name": "myFunc",
          "params": ["n"],
          "body": [
            { "type": "ReturnStatement", "expression": {"type": "LiteralExpression", "value": 123} }
          ]
        }
      ]
    }

    emitter = WasmEmitter()
    result = emitter.emit_program(ast)

    # Check some expected lines
    assert '(func $myFunc (param i32) (result i32' in result
    assert 'i32.const 123' in result
    assert 'return' in result
    assert '(export "main"' not in result  # no main function
