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
  (func $__top_level__
    i32.const 1024
    i32.const 1057
    call $llm
    call $print_string
    i32.const 1066
    call $print_string
  )
  (export "__top_level__" (func $__top_level__))
  (data (i32.const 1024) "\77\72\69\74\65\20\6d\65\20\61\20\6c\69\6d\65\72\69\63\6b\20\61\62\6f\75\74\20\63\68\65\65\73\65\00")
  (data (i32.const 1057) "\6c\6c\61\6d\61\33\2e\32\00")
  (data (i32.const 1066) "\0a\00")
)
