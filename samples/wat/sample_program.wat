(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $demonstrateExtendedOperators (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.div_s
    call $print_i32
    local.get $a
    local.get $b
    i32.div_s
    call $print_i32
    local.get $a
    local.get $b
    i32.rem_s
    call $print_i32
    local.get $a
    local.get $a
    i32.const 1
    i32.add
    local.set $a
    call $print_i32
    local.get $a
    call $print_i32
    local.get $b
    local.get $b
    i32.const 1
    i32.sub
    local.set $b
    call $print_i32
    local.get $b
    call $print_i32
    local.get $a
    i32.const 3
    i32.add
    local.set $a
    local.get $a
    call $print_i32
    local.get $a
    call $print_i32
    local.get $b
    i32.const 2
    i32.sub
    local.set $b
    local.get $b
    call $print_i32
    local.get $b
    call $print_i32
    local.get $a
    i32.const 10
    i32.add
    local.set $a
    local.get $a
    call $print_i32
    local.get $a
    call $print_i32
    local.get $b
    i32.const 5
    i32.sub
    local.set $b
    local.get $b
    call $print_i32
    local.get $b
    call $print_i32
    local.get $b
    return
  )
  (func $__top_level__
    i32.const 3
    i32.const 5
    call $demonstrateExtendedOperators
    call $print_i32
    i32.const 10
    i32.const 10
    call $demonstrateExtendedOperators
    call $print_i32
    i32.const 12
    i32.const 2
    call $demonstrateExtendedOperators
    call $print_i32
    i32.const 6
    i32.const 6
    call $demonstrateExtendedOperators
    call $print_i32
  )
  (export "demonstrateExtendedOperators" (func $demonstrateExtendedOperators))
  (export "__top_level__" (func $__top_level__))
)
