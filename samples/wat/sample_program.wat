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
  (func $__top_level__
    (local $poem i32)
    (local $model i32)
    (local $prompt i32)
    i32.const 1024
    local.set $prompt
    local.get $prompt
    i32.const 1065
    local.set $model
    local.get $model
    call $llm
    local.set $poem
    i32.const 1071
    call $print_string
    local.get $poem
    call $print_string
    i32.const 1098
    call $print_string
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\57\72\69\74\65\20\6d\65\20\61\20\73\68\6f\72\74\20\70\6f\65\6d\20\61\62\6f\75\74\20\74\68\65\20\73\75\6e\72\69\73\65\2e\00")
  (data (i32.const 1065) "\67\70\74\2d\34\00")
  (data (i32.const 1071) "\3d\3d\3d\20\50\6f\65\6d\20\61\62\6f\75\74\20\53\75\6e\72\69\73\65\20\3d\3d\3d\00")
  (data (i32.const 1098) "\0a\00")
)
