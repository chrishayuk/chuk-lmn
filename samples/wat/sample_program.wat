(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (func $foo (param $n i32) (result i32)
    local.get $n
    i32.const 2
    i32.mul
    return
  )
  (func $typedDouble (param $nums i32) (result i32)
    i32.const 0
    return
  )
  (func $main (result i32)
    (local $colors i32_ptr)
    (local $greeting i32)
    (local $myArray i32_ptr)
    (local $typedNums i32_ptr)
    (local $user i32_json)
    i32.const Hello\n🌍 \"Earth\"!
    local.set $greeting
    local.get $greeting
    call $print_i32
    i32.const 0
    local.set $user
    ;; skipping string literal: User data:
    local.get $user
    call $print_i32
    i32.const 0
    local.set $colors
    ;; skipping string literal: Colors array:
    local.get $colors
    call $print_i32
    i32.const 0
    local.set $typedNums
    ;; skipping string literal: typedNums is
    local.get $typedNums
    call $print_i32
    ;; skipping string literal: typedDouble(typedNums) =>
    local.get $typedNums
    call $typedDouble
    call $print_i32
    i32.const 0
    local.set $myArray
    ;; skipping string literal: Native array with expressions:
    local.get $myArray
    call $print_i32
    i32.const 0
    return
  )
  (export "foo" (func $foo))
  (export "typedDouble" (func $typedDouble))
  (export "main" (func $main))
)
