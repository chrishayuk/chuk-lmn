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
  (func $add (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.add
    return
  )
  (func $subtract (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.sub
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
    (local $p i32)
    (local $q i32)
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
    i32.const 1058
    call $print_string
    i32.const 1060
    call $print_string
    local.get $x
    call $print_i32
    i32.const 1067
    call $print_string
    local.get $y
    call $print_i32
    i32.const 1072
    call $print_string
    local.get $x
    local.get $y
    call $add
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 1085
    call $print_string
    local.get $y
    call $print_i32
    i32.const 1092
    call $print_string
    local.get $x
    call $print_i32
    i32.const 1097
    call $print_string
    local.get $x
    local.get $y
    call $add
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 3
    local.set $p
    i32.const 5
    local.set $q
    i32.const 1123
    call $print_string
    local.get $p
    call $print_i32
    i32.const 1133
    call $print_string
    local.get $q
    call $print_i32
    i32.const 1135
    call $print_string
    local.get $p
    local.get $q
    call $subtract
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 1153
    call $print_string
    local.get $q
    call $print_i32
    i32.const 1163
    call $print_string
    local.get $p
    call $print_i32
    i32.const 1165
    call $print_string
    local.get $q
    local.get $p
    call $subtract
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 1191
    call $print_string
    local.get $p
    call $print_i32
    i32.const 1203
    call $print_string
    local.get $q
    call $print_i32
    i32.const 1208
    call $print_string
    local.get $p
    local.get $q
    call $subtract
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 1221
    call $print_string
    local.get $p
    call $print_i32
    i32.const 1233
    call $print_string
    local.get $q
    call $print_i32
    i32.const 1238
    call $print_string
    local.get $q
    local.get $p
    call $subtract
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 5
    local.set $n
    i32.const 1264
    call $print_string
    local.get $n
    call $print_i32
    i32.const 1275
    call $print_string
    local.get $n
    call $factorial
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 1293
    call $print_string
    local.get $n
    call $print_i32
    i32.const 1306
    call $print_string
    local.get $n
    call $factorial
    call $print_i32
    i32.const 1058
    call $print_string
    i32.const 10
    local.set $z
    local.get $z
    call $print_i32
    i32.const 1319
    call $print_string
    local.get $z
    call $even_or_odd
    call $print_string
    i32.const 1058
    call $print_string
    i32.const 7
    local.set $w
    local.get $w
    call $print_i32
    i32.const 1324
    call $print_string
    local.get $w
    call $even_or_odd
    call $print_string
    i32.const 1058
    call $print_string
    i32.const 0
    return
  )
  (export "add" (func $add))
  (export "subtract" (func $subtract))
  (export "factorial" (func $factorial))
  (export "even_or_odd" (func $even_or_odd))
  (export "main" (func $main))
  (data (i32.const 1024) "\65\76\65\6e\00")
  (data (i32.const 1029) "\6f\64\64\00")
  (data (i32.const 1033) "\61\64\64\28\00")
  (data (i32.const 1038) "\2c\00")
  (data (i32.const 1040) "\29\20\5b\70\6f\73\69\74\69\6f\6e\61\6c\5d\20\3d\20\00")
  (data (i32.const 1058) "\0a\00")
  (data (i32.const 1060) "\61\64\64\28\61\3d\00")
  (data (i32.const 1067) "\2c\20\62\3d\00")
  (data (i32.const 1072) "\29\20\5b\6e\61\6d\65\64\5d\20\3d\20\00")
  (data (i32.const 1085) "\61\64\64\28\62\3d\00")
  (data (i32.const 1092) "\2c\20\61\3d\00")
  (data (i32.const 1097) "\29\20\5b\6e\61\6d\65\64\20\6f\75\74\20\6f\66\20\6f\72\64\65\72\5d\20\3d\20\00")
  (data (i32.const 1123) "\73\75\62\74\72\61\63\74\28\00")
  (data (i32.const 1133) "\2c\00")
  (data (i32.const 1135) "\29\20\5b\70\6f\73\69\74\69\6f\6e\61\6c\5d\20\3d\20\00")
  (data (i32.const 1153) "\73\75\62\74\72\61\63\74\28\00")
  (data (i32.const 1163) "\2c\00")
  (data (i32.const 1165) "\29\20\5b\70\6f\73\69\74\69\6f\6e\61\6c\20\73\77\61\70\70\65\64\5d\20\3d\20\00")
  (data (i32.const 1191) "\73\75\62\74\72\61\63\74\28\61\3d\00")
  (data (i32.const 1203) "\2c\20\62\3d\00")
  (data (i32.const 1208) "\29\20\5b\6e\61\6d\65\64\5d\20\3d\20\00")
  (data (i32.const 1221) "\73\75\62\74\72\61\63\74\28\62\3d\00")
  (data (i32.const 1233) "\2c\20\61\3d\00")
  (data (i32.const 1238) "\29\20\5b\6e\61\6d\65\64\20\6f\75\74\20\6f\66\20\6f\72\64\65\72\5d\20\3d\20\00")
  (data (i32.const 1264) "\66\61\63\74\6f\72\69\61\6c\28\00")
  (data (i32.const 1275) "\29\20\5b\70\6f\73\69\74\69\6f\6e\61\6c\5d\20\3d\20\00")
  (data (i32.const 1293) "\66\61\63\74\6f\72\69\61\6c\28\6e\3d\00")
  (data (i32.const 1306) "\29\20\5b\6e\61\6d\65\64\5d\20\3d\20\00")
  (data (i32.const 1319) "\20\69\73\20\00")
  (data (i32.const 1324) "\20\69\73\20\00")
)
