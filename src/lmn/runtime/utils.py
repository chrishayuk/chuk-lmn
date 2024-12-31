# file: src/lmn/runtime/utils.py

import re

def extract_lmn_code(text: str) -> list[str]:
    """
    Finds fenced code blocks of the form:
    
    ```lmn
    code...
    ```
    
    Returns a list of code snippet strings.
    """
    pattern = re.compile(r"```lmn\s+(.*?)```", re.DOTALL)
    matches = pattern.findall(text)
    return [m.strip() for m in matches if m.strip()]
