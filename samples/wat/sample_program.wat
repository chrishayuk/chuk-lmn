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
  (func $hello_llm (param $message i32) (result i32)
    (local $result i32)
    local.get $message
    i32.const 1024
    call $llm
    local.set $result
    local.get $result
    return
  )
  (func $__top_level__
    (local $y i32)
    (local $z i32)
    i32.const 1033
    call $hello_llm
    local.set $y
    local.get $y
    call $print_string
    i32.const 1063
    call $print_string
    i32.const 1065
    call $hello_llm
    local.set $z
    local.get $z
    call $print_string
    i32.const 1063
    call $print_string
  )
  (export "hello_llm" (func $hello_llm))
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\6c\6c\61\6d\61\33\2e\32\00")
  (data (i32.const 1033) "\77\72\69\74\65\20\61\20\6c\69\6d\65\72\69\63\6b\20\61\62\6f\75\74\20\63\68\65\65\73\65\00")
  (data (i32.const 1063) "\0a\00")
  (data (i32.const 1065) "\68\65\6c\6c\6f\00")
)
