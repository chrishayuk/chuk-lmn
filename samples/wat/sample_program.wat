(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f32" (func $print_f32 (param f32)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (import "env" "print_string" (func $print_string (param i32)))
  (import "env" "print_json" (func $print_json (param i32)))
  (import "env" "print_string_array" (func $print_string_array (param i32)))
  (import "env" "print_i32_array" (func $print_i32_array (param i32)))
  (import "env" "print_i64_array" (func $print_i64_array (param i32)))
  (import "env" "print_f32_array" (func $print_f32_array (param i32)))
  (import "env" "print_f64_array" (func $print_f64_array (param i32)))
  (import "env" "llm" (func $llm (param i32 i32) (result i32)))
  (memory (export "memory") 1)
  (func $closure_adder (param $x i32) (result i32)
    i32.const 0
    return
  )
  (func $main (result i32)
    (local $add100 i32)
    (local $add5 i32)
    (local $result1 i32)
    (local $result2 i32)
    i32.const 5
    call $closure_adder
    local.set $add5
    i32.const 10
    call $add5
    local.set $result1
    i32.const 1024
    call $print_string
    local.get $result1
    call $print_i32
    i32.const 1037
    call $print_string
    i32.const 100
    call $closure_adder
    local.set $add100
    i32.const 42
    call $add100
    local.set $result2
    i32.const 1039
    call $print_string
    local.get $result2
    call $print_i32
    i32.const 1037
    call $print_string
    i32.const 0
    return
  )
  (export "closure_adder" (func $closure_adder))
  (export "main" (func $main))
  (data (i32.const 1024) "\61\64\64\35\28\31\30\29\20\3d\3e\20\00")
  (data (i32.const 1037) "\0a\00")
  (data (i32.const 1039) "\61\64\64\31\30\30\28\34\32\29\20\3d\3e\20\00")
)
