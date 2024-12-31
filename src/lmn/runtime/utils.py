# file: src/lmn/runtime/utils.py
import re

def extract_lmn_code(text: str) -> list[str]:
    """
    Looks for LMN code blocks in two forms:
      1) Triple-backtick style:
         ```lmn
         ... code ...
         ```
      2) Single-backtick style:
         `lmn
         ... code ...
         `
    Returns a list of unique code block strings, each stripped of whitespace.
    """

    # (A) Detect triple-backtick form
    pattern_triple = re.compile(r"```lmn\s+(.*?)```", re.DOTALL)
    code_triple = pattern_triple.findall(text)

    # (B) Detect single-backtick form
    pattern_single = re.compile(r"`lmn\s+([^`]+)`", re.DOTALL)
    code_single = pattern_single.findall(text)

    # Combine
    all_code = code_triple + code_single

    # Strip whitespace, ignore empty
    stripped = [block.strip() for block in all_code if block.strip()]

    # (C) Remove duplicates while preserving order
    unique_blocks = []
    seen = set()
    for block in stripped:
        if block not in seen:
            seen.add(block)
            unique_blocks.append(block)

    return unique_blocks
