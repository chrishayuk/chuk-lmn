(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (import "env" "print_string" (func $print_string (param i32)))
  (import "env" "print_json" (func $print_json (param i32)))
  (import "env" "print_array" (func $print_array (param i32)))
  (memory (export "memory") 1)
  (func $__top_level__
    (local $colors i32)
    (local $user i32)
    (local $x i32)
    (local $decVal f64)
    (local $bigNum i64)
    (local $greeting i32)
    (local $jsonData i32)
    i32.const 1024
    local.set $greeting
    local.get $greeting
    call $print_string
    i32.const 1038
    local.set $user
    i32.const 1067
    call $print_string
    local.get $user
    call $print_json
    i32.const 1078
    local.set $colors
    i32.const 1103
    call $print_string
    local.get $colors
    call $print_string
    i32.const 123
    local.set $x
    local.get $x
    call $print_i32
    i64.const 4294967298
    local.set $bigNum
    local.get $bigNum
    call $print_i64
    f64.const 3.14
    local.set $decVal
    local.get $decVal
    call $print_f64
    i32.const 1117
    local.set $jsonData
    i32.const 1170
    call $print_string
    local.get $jsonData
    call $print_json
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\48\65\6c\6c\6f\5c\6e\57\6f\72\6c\64\21\00")
  (data (i32.const 1038) "\7b\22\6e\61\6d\65\22\3a\20\22\41\6c\69\63\65\22\2c\20\22\61\67\65\22\3a\20\34\32\7d\00")
  (data (i32.const 1067) "\55\73\65\72\20\64\61\74\61\3a\00")
  (data (i32.const 1078) "\5b\22\72\65\64\22\2c\20\22\67\72\65\65\6e\22\2c\20\22\62\6c\75\65\22\5d\00")
  (data (i32.const 1103) "\43\6f\6c\6f\72\73\20\61\72\72\61\79\3a\00")
  (data (i32.const 1117) "\7b\22\66\6f\6f\22\3a\20\22\62\61\72\22\2c\20\22\6e\75\6d\73\22\3a\20\5b\31\30\2c\20\32\30\2c\20\33\30\5d\2c\20\22\61\63\74\69\76\65\22\3a\20\74\72\75\65\7d\00")
  (data (i32.const 1170) "\6a\73\6f\6e\44\61\74\61\3a\00")
)
