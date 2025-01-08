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
  (func $fib (param $n i32) (result i32)
    local.get $n
    i32.const 2
    i32.lt_s
    if
    local.get $n
    return
    else
    local.get $n
    i32.const 1
    i32.sub
    call $fib
    local.get $n
    i32.const 2
    i32.sub
    call $fib
    i32.add
    return
    end
    i32.const 0
    return
  )
  (func $main (result i32)
    (local $x i32)
    i32.const 10
    local.set $x
    i32.const 1024
    call $print_string
    local.get $x
    call $print_i32
    i32.const 1037
    call $print_string
    local.get $x
    call $fib
    call $print_i32
    i32.const 1040
    call $print_string
    i32.const 0
    return
  )
  (export "fib" (func $fib))
  (export "main" (func $main))
  (data (i32.const 1024) "\46\69\62\6f\6e\61\63\63\69\20\6f\66\00")
  (data (i32.const 1037) "\69\73\00")
  (data (i32.const 1040) "\0a\00")
)
