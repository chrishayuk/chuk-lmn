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
  (import "env" "llm" (func $llm (param i32 i32) (result i32)))
  (memory (export "memory") 1)
  (func $__top_level__
    (local $typedColors i32)
    (local $typedUser i32)
    (local $typedBigNum i64)
    (local $user i32)
    (local $typedJsonData i32)
    (local $greeting i32)
    (local $colors i32)
    (local $decVal f64)
    (local $x i32)
    (local $jsonData i32)
    (local $typedDecVal f32)
    (local $typedX i32)
    (local $bigNum i64)
    (local $typedGreeting i32)
    i32.const 1024
    local.set $greeting
    local.get $greeting
    call $print_string
    i32.const 1038
    call $print_string
    i32.const 1040
    local.set $typedGreeting
    local.get $typedGreeting
    call $print_string
    i32.const 1038
    call $print_string
    i32.const 1058
    local.set $user
    i32.const 1087
    call $print_string
    local.get $user
    call $print_json
    i32.const 1038
    call $print_string
    i32.const 1098
    local.set $typedUser
    i32.const 1127
    call $print_string
    local.get $typedUser
    call $print_json
    i32.const 1038
    call $print_string
    i32.const 1161
    local.set $colors
    i32.const 1177
    call $print_string
    local.get $colors
    call $print_string_array
    i32.const 1038
    call $print_string
    i32.const 1217
    local.set $typedColors
    i32.const 1233
    call $print_string
    local.get $typedColors
    call $print_string_array
    i32.const 1038
    call $print_string
    i32.const 123
    local.set $x
    local.get $x
    call $print_i32
    i32.const 1038
    call $print_string
    i32.const 123
    local.set $typedX
    local.get $typedX
    call $print_i32
    i32.const 1038
    call $print_string
    i64.const 4294967298
    local.set $bigNum
    local.get $bigNum
    call $print_i64
    i32.const 1038
    call $print_string
    i64.const 4294967298
    local.set $typedBigNum
    local.get $typedBigNum
    call $print_i64
    i32.const 1038
    call $print_string
    f64.const 3.14
    local.set $decVal
    local.get $decVal
    call $print_f64
    i32.const 1038
    call $print_string
    f32.const 3.14
    local.set $typedDecVal
    local.get $typedDecVal
    call $print_f32
    i32.const 1038
    call $print_string
    i32.const 1255
    local.set $jsonData
    i32.const 1308
    call $print_string
    local.get $jsonData
    call $print_json
    i32.const 1038
    call $print_string
    i32.const 1329
    local.set $typedJsonData
    i32.const 1382
    call $print_string
    local.get $typedJsonData
    call $print_json
    i32.const 1038
    call $print_string
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\48\65\6c\6c\6f\5c\6e\57\6f\72\6c\64\21\00")
  (data (i32.const 1038) "\0a\00")
  (data (i32.const 1040) "\48\65\6c\6c\6f\20\74\79\70\65\64\20\77\6f\72\6c\64\00")
  (data (i32.const 1058) "\7b\22\6e\61\6d\65\22\3a\20\22\41\6c\69\63\65\22\2c\20\22\61\67\65\22\3a\20\34\32\7d\00")
  (data (i32.const 1087) "\55\73\65\72\20\64\61\74\61\3a\00")
  (data (i32.const 1098) "\7b\22\6e\61\6d\65\22\3a\20\22\41\6c\69\63\65\22\2c\20\22\61\67\65\22\3a\20\34\32\7d\00")
  (data (i32.const 1127) "\55\73\65\72\20\64\61\74\61\20\28\74\79\70\65\64\29\3a\00")
  (data (i32.const 1146) "\72\65\64\00")
  (data (i32.const 1150) "\67\72\65\65\6e\00")
  (data (i32.const 1156) "\62\6c\75\65\00")
  (data (i32.const 1161) "\03\00\00\00\7a\04\00\00\7e\04\00\00\84\04\00\00")
  (data (i32.const 1177) "\43\6f\6c\6f\72\73\20\61\72\72\61\79\20\28\69\6e\66\65\72\72\65\64\29\3a\00")
  (data (i32.const 1202) "\72\65\64\00")
  (data (i32.const 1206) "\67\72\65\65\6e\00")
  (data (i32.const 1212) "\62\6c\75\65\00")
  (data (i32.const 1217) "\03\00\00\00\b2\04\00\00\b6\04\00\00\bc\04\00\00")
  (data (i32.const 1233) "\43\6f\6c\6f\72\73\20\61\72\72\61\79\20\28\74\79\70\65\64\29\3a\00")
  (data (i32.const 1255) "\7b\22\66\6f\6f\22\3a\20\22\62\61\72\22\2c\20\22\6e\75\6d\73\22\3a\20\5b\31\30\2c\20\32\30\2c\20\33\30\5d\2c\20\22\61\63\74\69\76\65\22\3a\20\74\72\75\65\7d\00")
  (data (i32.const 1308) "\6a\73\6f\6e\44\61\74\61\20\28\69\6e\66\65\72\72\65\64\29\3a\00")
  (data (i32.const 1329) "\7b\22\66\6f\6f\22\3a\20\22\62\61\72\22\2c\20\22\6e\75\6d\73\22\3a\20\5b\31\30\2c\20\32\30\2c\20\33\30\5d\2c\20\22\61\63\74\69\76\65\22\3a\20\74\72\75\65\7d\00")
  (data (i32.const 1382) "\6a\73\6f\6e\44\61\74\61\20\28\74\79\70\65\64\29\3a\00")
)
