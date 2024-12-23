(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (func $main (result i32)
    i32.const 42
    call $print_i32
    i32.const 0
    return
  )
  (export "main" (func $main))
)
