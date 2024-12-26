(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (func $__top_level__
    i32.const 42
    call $print_i32
  )
  (export "__top_level__" (func $__top_level__))
)
