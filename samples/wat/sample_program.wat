(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $__top_level__
    (local $flt f32)
    (local $dbl2 f64)
    (local $dbl f64)
    (local $i64var i64)
    (local $i32var i32)
    f32.const 0
    local.set $flt
    f64.const 3.14159
    local.set $dbl
    i32.const 0
    local.set $i32var
    i64.const 10000000000
    local.set $i64var
    f64.const 0
    local.set $dbl2
    local.get $flt
    f64.promote_f32
    call $print_f64
    local.get $dbl
    call $print_f64
    local.get $i32var
    call $print_i32
    local.get $i64var
    call $print_i64
    local.get $dbl2
    call $print_f64
  )
  (export "__top_level__" (func $__top_level__))
)
