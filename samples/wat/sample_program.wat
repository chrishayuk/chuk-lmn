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
  (memory (export "memory") 1)
  (func $__top_level__
    (local $x i32)
    (local $tmpVal i32)
    (local $arr i32)
    i32.const 16
    call $malloc     ;; allocate dynamic array of that size
    local.set $arr   ;; store base pointer in $arr
    local.get $arr
    i32.const 0
    i32.add
    i32.const 3
    i32.store
    i32.const 1024
    local.set $tmpVal
    local.get $arr
    i32.const 4
    i32.add
    local.get $tmpVal
    i32.store
    i32.const 1026
    i32.const 1029
    call $llm
    local.set $tmpVal
    local.get $arr
    i32.const 8
    i32.add
    local.get $tmpVal
    i32.store
    i32.const 1038
    local.set $tmpVal
    local.get $arr
    i32.const 12
    i32.add
    local.get $tmpVal
    i32.store
    local.get $arr
    local.set $x
    local.get $x
    call $print_string_array
    i32.const 1040
    call $print_string
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\61\00")
  (data (i32.const 1026) "\68\69\00")
  (data (i32.const 1029) "\6c\6c\61\6d\61\33\2e\32\00")
  (data (i32.const 1038) "\63\00")
  (data (i32.const 1040) "\0a\00")
)
