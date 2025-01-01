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
  (func $__top_level__
    (local $inferredFloat f64)
    (local $inferredIntArray i32)
    (local $typedNestedJson i32)
    (local $inferredLong i64)
    (local $inferredInt i32)
    (local $inferredLongArray i32)
    (local $typedFloatArray i32)
    (local $inferredDoubleArray i32)
    (local $inferredJson i32)
    (local $typedIntArray i32)
    (local $typedString i32)
    (local $inferredDouble f64)
    (local $typedFloat f32)
    (local $typedInt i32)
    (local $typedDoubleArray i32)
    (local $inferredJsonArray i32)
    (local $typedStringArray i32)
    (local $typedDouble f64)
    (local $inferredFloatArray i32)
    (local $typedJson i32)
    (local $inferredString i32)
    (local $typedLongArray i32)
    (local $inferredNestedJson i32)
    (local $inferredStringArray i32)
    (local $typedJsonArray i32)
    (local $typedLong i64)
    i32.const 42
    local.set $typedInt
    local.get $typedInt
    call $print_i32
    i32.const 100
    local.set $inferredInt
    local.get $inferredInt
    call $print_i32
    f32.const 3.14
    local.set $typedFloat
    local.get $typedFloat
    call $print_f32
    f64.const 2.71828
    local.set $inferredFloat
    local.get $inferredFloat
    call $print_f64
    f64.const 123.456
    local.set $typedDouble
    local.get $typedDouble
    call $print_f64
    f64.const 0.000123
    local.set $inferredDouble
    local.get $inferredDouble
    call $print_f64
    i64.const 12345678901
    local.set $typedLong
    local.get $typedLong
    call $print_i64
    i64.const 98765432100
    local.set $inferredLong
    local.get $inferredLong
    call $print_i64
    i32.const 1024
    local.set $typedIntArray
    i32.const 1044
    call $print_string
    local.get $typedIntArray
    call $print_i32_array
    i32.const 1061
    local.set $inferredIntArray
    i32.const 1077
    call $print_string
    local.get $inferredIntArray
    call $print_i32_array
    i32.const 1097
    local.set $typedFloatArray
    i32.const 1113
    call $print_string
    local.get $typedFloatArray
    call $print_f32_array
    i32.const 1132
    local.set $inferredFloatArray
    i32.const 1160
    call $print_string
    local.get $inferredFloatArray
    call $print_f64_array
    i32.const 1182
    local.set $typedDoubleArray
    i32.const 1210
    call $print_string
    local.get $typedDoubleArray
    call $print_f64_array
    i32.const 1230
    local.set $inferredDoubleArray
    i32.const 1258
    call $print_string
    local.get $inferredDoubleArray
    call $print_f64_array
    i32.const 1281
    local.set $typedLongArray
    i32.const 1309
    call $print_string
    local.get $typedLongArray
    call $print_i64_array
    i32.const 1327
    local.set $inferredLongArray
    i32.const 1355
    call $print_string
    local.get $inferredLongArray
    call $print_i64_array
    i32.const 1376
    local.set $typedString
    local.get $typedString
    call $print_string
    i32.const 1401
    local.set $inferredString
    local.get $inferredString
    call $print_string
    i32.const 1445
    local.set $typedStringArray
    i32.const 1461
    call $print_string
    local.get $typedStringArray
    call $print_string_array
    i32.const 1487
    local.set $inferredStringArray
    i32.const 1503
    call $print_string
    local.get $inferredStringArray
    call $print_string_array
    i32.const 1526
    local.set $typedJson
    i32.const 1554
    call $print_string
    local.get $typedJson
    call $print_json
    i32.const 1573
    local.set $inferredJson
    i32.const 1606
    call $print_string
    local.get $inferredJson
    call $print_json
    i32.const 1628
    local.set $typedJsonArray
    i32.const 1684
    call $print_string
    local.get $typedJsonArray
    call $print_json
    i32.const 1702
    local.set $inferredJsonArray
    i32.const 1787
    call $print_string
    local.get $inferredJsonArray
    call $print_json
    i32.const 1808
    local.set $typedNestedJson
    i32.const 1948
    call $print_string
    local.get $typedNestedJson
    call $print_json
    i32.const 1967
    local.set $inferredNestedJson
    i32.const 2059
    call $print_string
    local.get $inferredNestedJson
    call $print_json
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\04\00\00\00\01\00\00\00\02\00\00\00\03\00\00\00\04\00\00\00")
  (data (i32.const 1044) "\54\79\70\65\64\20\69\6e\74\20\61\72\72\61\79\3a\00")
  (data (i32.const 1061) "\03\00\00\00\0a\00\00\00\14\00\00\00\1e\00\00\00")
  (data (i32.const 1077) "\49\6e\66\65\72\72\65\64\20\69\6e\74\20\61\72\72\61\79\3a\00")
  (data (i32.const 1097) "\03\00\00\00\00\00\c0\3f\00\00\10\40\00\00\70\40")
  (data (i32.const 1113) "\54\79\70\65\64\20\66\6c\6f\61\74\20\61\72\72\61\79\3a\00")
  (data (i32.const 1132) "\03\00\00\00\00\00\00\00\00\00\e0\3f\00\00\00\00\00\00\e8\3f\66\66\66\66\66\66\ee\3f")
  (data (i32.const 1160) "\49\6e\66\65\72\72\65\64\20\66\6c\6f\61\74\20\61\72\72\61\79\3a\00")
  (data (i32.const 1182) "\03\00\00\00\33\33\33\33\33\33\24\40\33\33\33\33\33\33\34\40\cd\cc\cc\cc\cc\4c\3e\40")
  (data (i32.const 1210) "\54\79\70\65\64\20\64\6f\75\62\6c\65\20\61\72\72\61\79\3a\00")
  (data (i32.const 1230) "\03\00\00\00\72\8a\8e\e4\f2\ff\23\40\d4\2b\65\19\e2\38\56\40\cb\10\c7\ba\38\4e\88\40")
  (data (i32.const 1258) "\49\6e\66\65\72\72\65\64\20\64\6f\75\62\6c\65\20\61\72\72\61\79\3a\00")
  (data (i32.const 1281) "\03\00\00\00\00\e4\0b\54\02\00\00\00\00\c8\17\a8\04\00\00\00\00\ac\23\fc\06\00\00\00")
  (data (i32.const 1309) "\54\79\70\65\64\20\6c\6f\6e\67\20\61\72\72\61\79\3a\00")
  (data (i32.const 1327) "\03\00\00\00\c7\19\46\96\02\00\00\00\8e\33\8c\2c\05\00\00\00\55\4d\d2\c2\07\00\00\00")
  (data (i32.const 1355) "\49\6e\66\65\72\72\65\64\20\6c\6f\6e\67\20\61\72\72\61\79\3a\00")
  (data (i32.const 1376) "\48\65\6c\6c\6f\20\66\72\6f\6d\20\74\79\70\65\64\20\73\74\72\69\6e\67\21\00")
  (data (i32.const 1401) "\48\65\6c\6c\6f\20\66\72\6f\6d\20\69\6e\66\65\72\72\65\64\20\73\74\72\69\6e\67\21\00")
  (data (i32.const 1429) "\41\6c\69\63\65\00")
  (data (i32.const 1435) "\42\6f\62\00")
  (data (i32.const 1439) "\43\61\72\6f\6c\00")
  (data (i32.const 1445) "\03\00\00\00\95\05\00\00\9b\05\00\00\9f\05\00\00")
  (data (i32.const 1461) "\54\79\70\65\64\20\73\74\72\69\6e\67\20\61\72\72\61\79\3a\00")
  (data (i32.const 1481) "\58\00")
  (data (i32.const 1483) "\59\00")
  (data (i32.const 1485) "\5a\00")
  (data (i32.const 1487) "\03\00\00\00\c9\05\00\00\cb\05\00\00\cd\05\00\00")
  (data (i32.const 1503) "\49\6e\66\65\72\72\65\64\20\73\74\72\69\6e\67\20\61\72\72\61\79\3a\00")
  (data (i32.const 1526) "\7b\22\66\6f\6f\22\3a\20\22\62\61\72\22\2c\20\22\63\6f\75\6e\74\22\3a\20\34\32\7d\00")
  (data (i32.const 1554) "\54\79\70\65\64\20\73\69\6e\67\6c\65\20\4a\53\4f\4e\3a\00")
  (data (i32.const 1573) "\7b\22\68\65\6c\6c\6f\22\3a\20\22\77\6f\72\6c\64\22\2c\20\22\76\61\6c\75\65\22\3a\20\39\39\39\7d\00")
  (data (i32.const 1606) "\49\6e\66\65\72\72\65\64\20\73\69\6e\67\6c\65\20\4a\53\4f\4e\3a\00")
  (data (i32.const 1628) "\5b\7b\22\69\64\22\3a\20\31\2c\20\22\61\63\74\69\76\65\22\3a\20\74\72\75\65\7d\2c\20\7b\22\69\64\22\3a\20\32\2c\20\22\61\63\74\69\76\65\22\3a\20\66\61\6c\73\65\7d\5d\00")
  (data (i32.const 1684) "\54\79\70\65\64\20\4a\53\4f\4e\20\61\72\72\61\79\3a\00")
  (data (i32.const 1702) "\5b\7b\22\70\6c\61\6e\65\74\22\3a\20\22\45\61\72\74\68\22\2c\20\22\70\6f\70\75\6c\61\74\69\6f\6e\22\3a\20\38\30\30\30\30\30\30\30\30\30\7d\2c\20\7b\22\70\6c\61\6e\65\74\22\3a\20\22\4d\61\72\73\22\2c\20\22\70\6f\70\75\6c\61\74\69\6f\6e\22\3a\20\30\7d\5d\00")
  (data (i32.const 1787) "\49\6e\66\65\72\72\65\64\20\4a\53\4f\4e\20\61\72\72\61\79\3a\00")
  (data (i32.const 1808) "\7b\22\64\65\70\61\72\74\6d\65\6e\74\73\22\3a\20\5b\7b\22\6e\61\6d\65\22\3a\20\22\45\6e\67\69\6e\65\65\72\69\6e\67\22\2c\20\22\6d\65\6d\62\65\72\73\22\3a\20\5b\22\41\6c\69\63\65\22\2c\20\22\42\6f\62\22\5d\7d\2c\20\7b\22\6e\61\6d\65\22\3a\20\22\44\65\73\69\67\6e\22\2c\20\22\6d\65\6d\62\65\72\73\22\3a\20\5b\22\43\61\72\6f\6c\22\2c\20\22\44\61\76\65\22\5d\7d\5d\2c\20\22\6c\6f\63\61\74\69\6f\6e\22\3a\20\22\48\51\22\7d\00")
  (data (i32.const 1948) "\54\79\70\65\64\20\6e\65\73\74\65\64\20\4a\53\4f\4e\3a\00")
  (data (i32.const 1967) "\7b\22\6d\65\74\61\64\61\74\61\22\3a\20\7b\22\76\65\72\73\69\6f\6e\22\3a\20\31\2c\20\22\74\61\67\73\22\3a\20\5b\22\69\6e\66\65\72\72\65\64\22\2c\20\22\74\65\73\74\22\5d\7d\2c\20\22\64\61\74\61\22\3a\20\7b\22\69\74\65\6d\73\22\3a\20\5b\31\30\2c\20\32\30\2c\20\33\30\5d\7d\7d\00")
  (data (i32.const 2059) "\49\6e\66\65\72\72\65\64\20\6e\65\73\74\65\64\20\4a\53\4f\4e\3a\00")
)
