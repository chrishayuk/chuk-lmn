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
  (memory (export "memory") 1)
  (func $demonstrateBreakContinue (param $n i32) (param $arr i32) (result i32)
    (local $i i32)
    i32.const 1024
    call $print_string
    i32.const 1074
    call $print_string
    i32.const 1
    local.set $i
    block $for_exit
      loop $for_loop
    local.get $i
    local.get $n
    i32.lt_s
    i32.eqz
    br_if $for_exit
    block $for_continue
    local.get $i
    i32.const 3
    i32.eq
    if
    i32.const 1076
    call $print_string
    i32.const 1074
    call $print_string
    br $for_exit
    end
    local.get $i
    i32.const 2
    i32.rem_s
    i32.const 0
    i32.eq
    if
    i32.const 1094
    call $print_string
    local.get $i
    call $print_i32
    i32.const 1074
    call $print_string
    br $for_continue
    end
    i32.const 1113
    call $print_string
    local.get $i
    call $print_i32
    i32.const 1074
    call $print_string
    end $for_continue
    local.get $i
    i32.const 1
    i32.add
    local.set $i
    br $for_loop
    end
    end
    i32.const 0
    return
  )
  (func $main (result i32)
    (local $n i32)
    (local $nums i32)
    i32.const 5
    local.set $n
    i32.const 1126
    local.set $nums
    local.get $n
    local.get $nums
    call $demonstrateBreakContinue
    i32.const 0
    return
  )
  (export "demonstrateBreakContinue" (func $demonstrateBreakContinue))
  (export "main" (func $main))
  (data (i32.const 1024) "\3d\3d\3d\20\52\61\6e\67\65\2d\62\61\73\65\64\20\66\6f\72\20\6c\6f\6f\70\20\28\31\2e\2e\6e\29\20\64\65\6d\6f\6e\73\74\72\61\74\69\6f\6e\20\3d\3d\3d\00")
  (data (i32.const 1074) "\0a\00")
  (data (i32.const 1076) "\42\72\65\61\6b\69\6e\67\20\61\74\20\69\20\3d\20\33\00")
  (data (i32.const 1094) "\53\6b\69\70\70\69\6e\67\20\65\76\65\6e\20\69\20\3d\20\00")
  (data (i32.const 1113) "\43\75\72\72\65\6e\74\20\69\20\3d\20\00")
  (data (i32.const 1126) "\5b\31\2c\20\32\2c\20\30\2c\20\34\2c\20\22\3c\65\78\70\72\3a\55\6e\61\72\79\45\78\70\72\65\73\73\69\6f\6e\3e\22\2c\20\35\5d\00")
)
