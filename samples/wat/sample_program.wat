(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $checkNumericConditions (param $x i32) (result i32)
    local.get $x
    i32.const 10
    i32.gt_s
    if
    i32.const 999
    call $print_i32
    else
    local.get $x
    i32.const 10
    i32.eq
      if
    i32.const 1000
    call $print_i32
      else
    i32.const 888
    call $print_i32
      end
    end
    local.get $x
    i32.const 5
    i32.add
    i32.const 10
    i32.lt_s
    if
    local.get $x
    i32.const 5
    i32.add
    call $print_i32
    else
    end
    local.get $x
    i32.const 42
    i32.add
    return
  )
  (func $__top_level__
    i32.const 8
    call $print_i32
    i32.const 8
    call $checkNumericConditions
    call $print_i32
    i32.const 10
    call $print_i32
    i32.const 10
    call $checkNumericConditions
    call $print_i32
    i32.const 12
    call $print_i32
    i32.const 12
    call $checkNumericConditions
    call $print_i32
  )
  (export "checkNumericConditions" (func $checkNumericConditions))
  (export "__top_level__" (func $__top_level__))
)
