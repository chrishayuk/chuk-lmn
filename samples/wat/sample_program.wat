(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $__top_level__
    (local $negative i32)
    (local $smallVal i32)
    (local $inferredLarge i64)
    (local $ratio f32)
    (local $eVal f64)
    (local $inferredRatio f64)
    (local $inferredInt i32)
    (local $bigVal i64)
    (local $inferredNegative i32)
    i32.const 0
    local.set $smallVal
    i64.const 0
    local.set $bigVal
    f32.const 0
    local.set $ratio
    f64.const 0
    local.set $eVal
    i32.const 0
    local.set $negative
    i32.const 42
    local.set $smallVal
    i64.const 2147483648
    local.set $bigVal
    f32.const 3.14
    local.set $ratio
    f64.const 2.71828
    local.set $eVal
    i32.const 42
    i32.const -1
    i32.mul
    local.set $negative
    i32.const 42
    local.set $inferredInt
    i64.const 9999999999999
    local.set $inferredLarge
    f64.const 0.5
    local.set $inferredRatio
    i32.const 100
    i32.const -1
    i32.mul
    local.set $inferredNegative
    local.get $smallVal
    call $print_i32
    local.get $bigVal
    call $print_i64
    local.get $ratio
    f64.promote_f32
    call $print_f64
    local.get $eVal
    call $print_f64
    local.get $negative
    call $print_i32
    local.get $inferredInt
    call $print_i32
    local.get $inferredLarge
    call $print_i64
    local.get $inferredRatio
    call $print_f64
    local.get $inferredNegative
    call $print_i32
  )
  (export "__top_level__" (func $__top_level__))
)
