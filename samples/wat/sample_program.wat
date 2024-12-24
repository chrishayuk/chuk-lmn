(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (func $main (result i32)
    (local $a i32)
    (local $b i32)
    (local $product i32)
    (local $sum i32)
    f64.const 5.3
    local.set $a
    f64.const 3.2
    local.set $b
    local.get $a
    local.get $b
    i32.add
    local.set $sum
    local.get $a
    local.get $b
    i32.mul
    local.set $product
    local.get $sum
    call $print_i32
    local.get $product
    call $print_i32
    i32.const 0
    return
  )
  (export "main" (func $main))
)
