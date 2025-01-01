# src/lmn/runtime/memory_utils.py
import struct

def read_utf8_string(store, memory, offset, max_len=200):
    """
    Reads a UTF-8 string from 'memory' starting at 'offset',
    stopping at a null byte or after max_len bytes.
    Returns the decoded Python string.
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset >= mem_size:
        return f"<invalid pointer {offset}>"

    raw_bytes = bytearray()
    end = min(offset + max_len, mem_size)
    for i in range(offset, end):
        b = mem_data[i]
        if b == 0:
            break
        raw_bytes.append(b)

    return raw_bytes.decode("utf-8", errors="replace")

def parse_i32_array(store, memory, offset):
    """
    Parses an i32 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:i32> <elem2:i32> ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 4 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+4])
        val = struct.unpack("<i", elem_bytes)[0]
        elements.append(val)
        offset += 4

    return elements

def parse_i64_array(store, memory, offset):
    """
    Parses an i64 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:i64> <elem2:i64> ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 8 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+8])
        val = struct.unpack("<q", elem_bytes)[0]
        elements.append(val)
        offset += 8

    return elements

def parse_f32_array(store, memory, offset):
    """
    Parses an f32 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:f32> <elem2:f32> ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 4 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+4])
        val = struct.unpack("<f", elem_bytes)[0]
        elements.append(val)
        offset += 4

    return elements

def parse_f64_array(store, memory, offset):
    """
    Parses an f64 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:f64> <elem2:f64> ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 8 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+8])
        val = struct.unpack("<d", elem_bytes)[0]
        elements.append(val)
        offset += 8

    return elements

def parse_i32_string_array(store, memory, offset):
    """
    Layout for i32_string_array:
      [ length : i32 ]
      [ pointer1 : i32 ]
      [ pointer2 : i32 ]
      ...
    Each pointer references a null-terminated UTF-8 string.
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    strings = []
    for _ in range(length):
        if offset + 4 > mem_size:
            strings.append("<out-of-bounds pointer>")
            break
        ptr_bytes = bytes(mem_data[offset:offset+4])
        ptr_val = struct.unpack("<i", ptr_bytes)[0]
        offset += 4

        text = read_utf8_string(store, memory, ptr_val)
        strings.append(text)

    return strings
