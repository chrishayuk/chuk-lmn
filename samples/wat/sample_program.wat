(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $sum (param $a i32) (param $b i32) (result i32)
    (local $result i32)
    i32.const 0
    local.set $result
    local.get $a
    local.get $b
    i32.add
    local.set $result
    local.get $result
    return
  )
  (func $__top_level__
    i32.const 10
    i32.const 20
    call $sum
    call $print_i32
  )
  (export "sum" (func $sum))
  (export "__top_level__" (func $__top_level__))
)
