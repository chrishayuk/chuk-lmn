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
  (func $factorial (param $n i32) (result i32)
    local.get $n
    i32.const 1
    i32.le_s
    if
    i32.const 1
    return
    else
    local.get $n
    local.get $n
    i32.const 1
    i32.sub
    call $factorial
    i32.mul
    return
    end
    i32.const 0
    return
  )
  (func $main (result i32)
    (local $x i32)
    i32.const 5
    local.set $x
    i32.const 1024
    call $print_string
    local.get $x
    call $print_i32
    i32.const 1038
    call $print_string
    local.get $x
    call $factorial
    call $print_i32
    i32.const 1043
    call $print_string
    i32.const 0
    return
  )
  (export "factorial" (func $factorial))
  (export "main" (func $main))
  (data (i32.const 1024) "\46\61\63\74\6f\72\69\61\6c\20\6f\66\20\00")
  (data (i32.const 1038) "\20\69\73\20\00")
  (data (i32.const 1043) "\0a\00")
)
