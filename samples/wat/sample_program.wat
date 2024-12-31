(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f32" (func $print_f32 (param f32)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (import "env" "print_string" (func $print_string (param i32)))
  (import "env" "print_json" (func $print_json (param i32)))
  (import "env" "print_array" (func $print_array (param i32)))
  (memory (export "memory") 1)
  (func $__top_level__
    (local $decVal f64)
    (local $colors i32)
    (local $x i32)
    (local $typedUser i32)
    (local $user i32)
    (local $typedJsonData i32)
    (local $typedDecVal f32)
    (local $bigNum i64)
    (local $greeting i32)
    (local $jsonData i32)
    (local $typedColors i32)
    (local $typedGreeting i32)
    (local $typedBigNum i64)
    (local $typedX i32)
    i32.const 1024
    local.set $greeting
    local.get $greeting
    call $print_string
    i32.const 1038
    local.set $typedGreeting
    local.get $typedGreeting
    call $print_string
    i32.const 1056
    local.set $user
    i32.const 1085
    call $print_string
    local.get $user
    call $print_json
    i32.const 1096
    local.set $typedUser
    i32.const 1125
    call $print_string
    local.get $typedUser
    call $print_json
    i32.const 1144
    local.set $colors
    i32.const 1169
    call $print_string
    local.get $colors
    call $print_string
    i32.const 1194
    local.set $typedColors
    i32.const 1219
    call $print_string
    local.get $typedColors
    call $print_string
    i32.const 123
    local.set $x
    local.get $x
    call $print_i32
    i32.const 123
    local.set $typedX
    local.get $typedX
    call $print_i32
    i64.const 4294967298
    local.set $bigNum
    local.get $bigNum
    call $print_i64
    i64.const 4294967298
    local.set $typedBigNum
    local.get $typedBigNum
    call $print_i64
    f64.const 3.14
    local.set $decVal
    local.get $decVal
    call $print_f64
    f32.const 3.14
    local.set $typedDecVal
    local.get $typedDecVal
    call $print_f32
    i32.const 1241
    local.set $jsonData
    i32.const 1294
    call $print_string
    local.get $jsonData
    call $print_json
    i32.const 1315
    local.set $typedJsonData
    i32.const 1368
    call $print_string
    local.get $typedJsonData
    call $print_json
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\48\65\6c\6c\6f\5c\6e\57\6f\72\6c\64\21\00")
  (data (i32.const 1038) "\48\65\6c\6c\6f\20\74\79\70\65\64\20\77\6f\72\6c\64\00")
  (data (i32.const 1056) "\7b\22\6e\61\6d\65\22\3a\20\22\41\6c\69\63\65\22\2c\20\22\61\67\65\22\3a\20\34\32\7d\00")
  (data (i32.const 1085) "\55\73\65\72\20\64\61\74\61\3a\00")
  (data (i32.const 1096) "\7b\22\6e\61\6d\65\22\3a\20\22\41\6c\69\63\65\22\2c\20\22\61\67\65\22\3a\20\34\32\7d\00")
  (data (i32.const 1125) "\55\73\65\72\20\64\61\74\61\20\28\74\79\70\65\64\29\3a\00")
  (data (i32.const 1144) "\5b\22\72\65\64\22\2c\20\22\67\72\65\65\6e\22\2c\20\22\62\6c\75\65\22\5d\00")
  (data (i32.const 1169) "\43\6f\6c\6f\72\73\20\61\72\72\61\79\20\28\69\6e\66\65\72\72\65\64\29\3a\00")
  (data (i32.const 1194) "\5b\22\72\65\64\22\2c\20\22\67\72\65\65\6e\22\2c\20\22\62\6c\75\65\22\5d\00")
  (data (i32.const 1219) "\43\6f\6c\6f\72\73\20\61\72\72\61\79\20\28\74\79\70\65\64\29\3a\00")
  (data (i32.const 1241) "\7b\22\66\6f\6f\22\3a\20\22\62\61\72\22\2c\20\22\6e\75\6d\73\22\3a\20\5b\31\30\2c\20\32\30\2c\20\33\30\5d\2c\20\22\61\63\74\69\76\65\22\3a\20\74\72\75\65\7d\00")
  (data (i32.const 1294) "\6a\73\6f\6e\44\61\74\61\20\28\69\6e\66\65\72\72\65\64\29\3a\00")
  (data (i32.const 1315) "\7b\22\66\6f\6f\22\3a\20\22\62\61\72\22\2c\20\22\6e\75\6d\73\22\3a\20\5b\31\30\2c\20\32\30\2c\20\33\30\5d\2c\20\22\61\63\74\69\76\65\22\3a\20\74\72\75\65\7d\00")
  (data (i32.const 1368) "\6a\73\6f\6e\44\61\74\61\20\28\74\79\70\65\64\29\3a\00")
)
