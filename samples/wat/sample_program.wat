(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f32" (func $print_f32 (param f32)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (import "env" "print_string" (func $print_string (param i32)))
  (import "env" "print_json" (func $print_json (param i32)))
  (import "env" "print_string_array" (func $print_string_array (param i32)))
  (import "env" "print_i32_array" (func $print_i32_array (param i32)))
  (import "env" "print_i64_array" (func $print_i64_array (param i32)))
  (import "env" "print_f32_array" (func $print_f32_array (param i32)))
  (import "env" "print_f64_array" (func $print_f64_array (param i32)))
  (memory (export "memory") 1)
  (func $add (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.add
    return
  )
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
  (func $even_or_odd (param $x i32) (result i32)
    local.get $x
    i32.const 2
    i32.rem_s
    i32.const 0
    i32.eq
    if
    i32.const 1024
    return
    else
    i32.const 1029
    return
    end
    i32.const 0
    return
  )
  (func $main (result i32)
    (local $n i32)
    (local $w i32)
    (local $x i32)
    (local $y i32)
    (local $z i32)
    i32.const 3
    local.set $x
    i32.const 5
    local.set $y
    i32.const 1033
    call $print_string
    local.get $x
    call $print_i32
    i32.const 1038
    call $print_string
    local.get $y
    call $print_i32
    i32.const 1040
    call $print_string
    local.get $x
    local.get $y
    call $add
    call $print_i32
    i32.const 1045
    call $print_string
    i32.const 5
    local.set $n
    i32.const 1047
    call $print_string
    local.get $n
    call $print_i32
    i32.const 1058
    call $print_string
    local.get $n
    call $factorial
    call $print_i32
    i32.const 1045
    call $print_string
    i32.const 10
    local.set $z
    local.get $z
    call $print_i32
    i32.const 1063
    call $print_string
    local.get $z
    call $even_or_odd
    call $print_string
    i32.const 1045
    call $print_string
    i32.const 7
    local.set $w
    local.get $w
    call $print_i32
    i32.const 1068
    call $print_string
    local.get $w
    call $even_or_odd
    call $print_string
    i32.const 1045
    call $print_string
    i32.const 0
    return
  )
  (export "add" (func $add))
  (export "factorial" (func $factorial))
  (export "even_or_odd" (func $even_or_odd))
  (export "main" (func $main))
  (data (i32.const 1024) "\65\76\65\6e\00")
  (data (i32.const 1029) "\6f\64\64\00")
  (data (i32.const 1033) "\61\64\64\28\00")
  (data (i32.const 1038) "\2c\00")
  (data (i32.const 1040) "\29\20\3d\20\00")
  (data (i32.const 1045) "\0a\00")
  (data (i32.const 1047) "\66\61\63\74\6f\72\69\61\6c\28\00")
  (data (i32.const 1058) "\29\20\3d\20\00")
  (data (i32.const 1063) "\20\69\73\20\00")
  (data (i32.const 1068) "\20\69\73\20\00")
)
