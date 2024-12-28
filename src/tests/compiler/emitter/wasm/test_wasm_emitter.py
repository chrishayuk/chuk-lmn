# file: tests/emitter/wasm/test_wasm_emitter.py
from lmn.compiler.emitter.wasm.wasm_emitter import WasmEmitter

def test_emit_program_with_function():
    ast = {
      "type": "Program",
      "body": [
        {
          "type": "FunctionDefinition",
          "name": "myFunc",
          "params": [
            {
              "type": "FunctionParameter",
              "name": "n",
              "type_annotation": "i32"
            }
          ],
          "body": [
            {
              "type": "ReturnStatement",
              "expression": {
                "type": "LiteralExpression",
                "value": 123
              }
            }
          ]
        }
      ]
    }

    emitter = WasmEmitter()
    result = emitter.emit_program(ast)

    # Check some expected lines

    # 1) The function signature:
    #    We now expect (func $myFunc (param $n i32) (result i32)
    #    because your emitter uses param dictionaries with 'name' and 'type_annotation'.
    assert '(func $myFunc (param $n i32) (result i32' in result

    # 2) The return expression:
    assert 'i32.const 123' in result
    assert 'return' in result

    # 3) We do NOT expect an export of main,
    #    since the function is named "myFunc", not "main".
    assert '(export "main"' not in result
