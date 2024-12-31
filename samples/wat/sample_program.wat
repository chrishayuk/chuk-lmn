(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f32" (func $print_f32 (param f32)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (import "env" "print_string" (func $print_string (param i32)))
  (import "env" "print_json" (func $print_json (param i32)))
  (import "env" "print_array" (func $print_array (param i32)))
  (memory (export "memory") 1)
  (func $__top_level__
    f32.const 2.71
    call $print_f32
  )
  (export "__top_level__" (func $__top_level__))
)
