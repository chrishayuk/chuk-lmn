(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $__top_level__
    i32.const 42
    call $print_i32
    i32.const 10
    call $print_i32
    f64.const 3.14
    call $print_f64
    i32.const 42
    i32.const 10
    i32.add
    call $print_i32
    i32.const 42
    i32.const 10
    i32.sub
    call $print_i32
    i32.const 42
    i32.const 10
    i32.mul
    call $print_i32
    i32.const 42
    i32.const 10
    i32.div_s
    call $print_i32
    i32.const 42
    i32.const -1
    i32.mul
    call $print_i32
    i32.const 42
    i32.const 10
    i32.add
    i32.const 2
    i32.mul
    call $print_i32
    i32.const 42
    i32.const 10
    i32.gt_s
    call $print_i32
  )
  (export "__top_level__" (func $__top_level__))
)
