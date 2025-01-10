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
  (import "env" "malloc" (func $malloc (param i32) (result i32)))
  (import "env" "parse_string_to_i32" (func $parse_string_to_i32 (param i32) (result i32)))
  (memory (export "memory") 1)
  (func $__top_level__
    (local $x i32)
    i32.const 1024
    i32.const 1067
    call $llm
    call $parse_string_to_i32
    local.set $x
    local.get $x
    i32.const 1
    i32.add
    local.set $x
    local.get $x
    call $print_i32
    i32.const 1076
    call $print_string
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\77\68\61\74\27\73\20\31\30\2b\35\3f\20\20\61\6e\73\77\65\72\20\6f\6e\6c\79\2c\20\6e\6f\20\65\78\70\6c\61\6e\61\74\69\6f\6e\73\00")
  (data (i32.const 1067) "\6c\6c\61\6d\61\33\2e\32\00")
  (data (i32.const 1076) "\0a\00")
)
