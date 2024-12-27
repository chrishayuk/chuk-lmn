(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $__top_level__
    (local $a i32)
    (local $sum i32)
    (local $difference i32)
    (local $product i32)
    (local $b i32)
    i32.const 5
    local.set $a
    i32.const 3
    local.set $b
    local.get $a
    local.get $b
    i32.add
    local.set $sum
    local.get $a
    local.get $b
    i32.mul
    local.set $product
    local.get $a
    local.get $b
    i32.sub
    local.set $difference
    local.get $sum
    call $print_i32
    local.get $product
    call $print_i32
    local.get $difference
    call $print_i32
  )
  (export "__top_level__" (func $__top_level__))
)
