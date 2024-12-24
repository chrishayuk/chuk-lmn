(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (func $factorial (param $n i32) (result i32)
    local.get $n
    i32.const 1
    i32.le_s
    if
    i32.const 1
    return
    else
    local.get $n
    local.get $n
    i32.const 1
    i32.sub
    call $factorial
    i32.mul
    return
    end
    i32.const 0
    return
  )
  (func $main (result i32)
    (local $x i32)
    i32.const 5
    local.set $x
    local.get $x
    call $print_i32
    local.get $x
    call $factorial
    call $print_i32
    i32.const 0
    return
  )
  (export "main" (func $main))
)
