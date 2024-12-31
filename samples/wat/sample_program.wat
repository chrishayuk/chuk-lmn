(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f32" (func $print_f32 (param f32)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (import "env" "print_string" (func $print_string (param i32)))
  (import "env" "print_json" (func $print_json (param i32)))
  (import "env" "print_i32_array" (func $print_i32_array (param i32)))
  (import "env" "print_i64_array" (func $print_i64_array (param i32)))
  (import "env" "print_f32_array" (func $print_f32_array (param i32)))
  (import "env" "print_f64_array" (func $print_f64_array (param i32)))
  (memory (export "memory") 1)
  (func $__top_level__
    (local $smallInts i32)
    (local $moreInts i32)
    (local $bigVals i32)
    (local $floatVals i32)
    (local $doubleVals i32)
    (local $user i32)
    i32.const 1024
    local.set $smallInts
    i32.const 1044
    call $print_string
    local.get $smallInts
    call $print_i32_array
    i32.const 1053
    local.set $bigVals
    i32.const 1081
    call $print_string
    local.get $bigVals
    call $print_i64_array
    i32.const 1091
    local.set $floatVals
    i32.const 1107
    call $print_string
    local.get $floatVals
    call $print_f32_array
    i32.const 1118
    local.set $doubleVals
    i32.const 1146
    call $print_string
    local.get $doubleVals
    call $print_f64_array
    i32.const 1158
    local.set $moreInts
    i32.const 1182
    call $print_string
    local.get $moreInts
    call $print_i32_array
    i32.const 1195
    local.set $user
    i32.const 1237
    call $print_string
    local.get $user
    call $print_json
    i32.const 1250
    call $print_string
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\04\00\00\00\01\00\00\00\02\00\00\00\03\00\00\00\2a\00\00\00")
  (data (i32.const 1044) "\69\6e\74\5b\5d\20\3d\3e\00")
  (data (i32.const 1053) "\03\00\00\00\00\00\00\80\00\00\00\00\02\00\00\00\01\00\00\00\ff\0f\a5\d4\e8\00\00\00")
  (data (i32.const 1081) "\6c\6f\6e\67\5b\5d\20\3d\3e\00")
  (data (i32.const 1091) "\03\00\00\00\00\00\80\3f\00\00\20\40\c3\f5\48\40")
  (data (i32.const 1107) "\66\6c\6f\61\74\5b\5d\20\3d\3e\00")
  (data (i32.const 1118) "\03\00\00\00\00\00\00\00\00\00\59\40\90\f7\aa\95\09\bf\05\40\0b\0b\ee\07\3c\dd\5e\40")
  (data (i32.const 1146) "\64\6f\75\62\6c\65\5b\5d\20\3d\3e\00")
  (data (i32.const 1158) "\05\00\00\00\00\00\00\00\00\00\00\00\0f\27\00\00\2a\00\00\00\a0\86\01\00")
  (data (i32.const 1182) "\6d\6f\72\65\20\69\6e\74\73\20\3d\3e\00")
  (data (i32.const 1195) "\7b\22\6e\61\6d\65\22\3a\20\22\41\6c\69\63\65\22\2c\20\22\69\64\73\22\3a\20\5b\31\30\31\2c\20\32\30\32\2c\20\33\30\33\5d\7d\00")
  (data (i32.const 1237) "\55\73\65\72\20\64\61\74\61\20\3d\3e\00")
  (data (i32.const 1250) "\45\6e\64\20\6f\66\20\74\79\70\65\64\20\61\72\72\61\79\73\20\74\65\73\74\21\00")
)
