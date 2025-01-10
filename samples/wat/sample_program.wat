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
  (import "env" "malloc" (func $malloc (param i32) (result i32)))
  (import "env" "parse_string_to_i32" (func $parse_string_to_i32 (param i32) (result i32)))
  (import "env" "get_internet_time" (func $get_internet_time (result i32)))
  (import "env" "get_system_time" (func $get_system_time (result i32)))
  (import "env" "get_weather" (func $get_weather (param f64 f64) (result i32)))
  (import "env" "get_joke" (func $get_joke (result i32)))
  (import "env" "ask_tools" (func $ask_tools (param i32) (result i32)))
  (import "env" "call_tools" (func $call_tools (param i32) (result i32)))
  (memory (export "memory") 1)
  (func $main (result i32)
    (local $poem i32)
    (local $story i32)
    i32.const 1024
    i32.const 1069
    call $llm
    local.set $poem
    i32.const 1078
    call $print_string
    i32.const 1113
    call $print_string
    local.get $poem
    call $print_string
    i32.const 1113
    call $print_string
    i32.const 1115
    call $print_string
    i32.const 1113
    call $print_string
    i32.const 1116
    i32.const 1161
    call $llm
    local.set $story
    i32.const 1185
    call $print_string
    i32.const 1113
    call $print_string
    local.get $story
    call $print_string
    i32.const 1113
    call $print_string
    i32.const 0
    return
  )
  (export "main" (func $main))
  (data (i32.const 1024) "\57\72\69\74\65\20\6d\65\20\61\20\73\68\6f\72\74\20\6c\69\6d\65\72\69\63\6b\20\61\62\6f\75\74\20\74\68\65\20\73\75\6e\72\69\73\65\2e\00")
  (data (i32.const 1069) "\6c\6c\61\6d\61\33\2e\32\00")
  (data (i32.const 1078) "\3d\3d\3d\20\50\6f\65\6d\20\61\62\6f\75\74\20\53\75\6e\72\69\73\65\20\28\6c\6c\61\6d\61\29\20\3d\3d\3d\00")
  (data (i32.const 1113) "\0a\00")
  (data (i32.const 1115) "\00")
  (data (i32.const 1116) "\57\72\69\74\65\20\6d\65\20\61\20\73\68\6f\72\74\20\6c\69\6d\65\72\69\63\6b\20\61\62\6f\75\74\20\74\68\65\20\73\75\6e\72\69\73\65\2e\00")
  (data (i32.const 1161) "\67\72\61\6e\69\74\65\33\2e\31\2d\64\65\6e\73\65\3a\6c\61\74\65\73\74\00")
  (data (i32.const 1185) "\3d\3d\3d\20\50\6f\65\6d\20\61\62\6f\75\74\20\53\75\6e\72\69\73\65\20\28\67\72\61\6e\69\74\65\29\20\3d\3d\3d\00")
)
