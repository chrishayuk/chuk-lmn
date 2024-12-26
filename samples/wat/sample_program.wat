(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $__top_level__
    i32.const 42
    call $print_i32
    i64.const 4294967296
    call $print_i64
    f64.const 3.14
    call $print_f64
  )
  (export "__top_level__" (func $__top_level__))
)
