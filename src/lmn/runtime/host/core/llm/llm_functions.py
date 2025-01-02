# src/lmn/runtime/core/llm/llm_functions.py
import wasmtime
from pathlib import Path

# Import the universal loader
from lmn.runtime.host.universal_host_loader import UniversalHostLoader

class LLMHostFunctions:
    def __init__(self, linker: wasmtime.Linker, store: wasmtime.Store, output_list: list, memory_ref=None):
        """
        Initializes and registers LLM-related host functions.
        """
        feature_folder = Path("src/lmn/runtime/host/core/llm")

        universal_loader = UniversalHostLoader(
            linker=linker,
            store=store,
            output_list=output_list,
            memory_ref=memory_ref,
            feature_folders=[feature_folder]
        )
        # That’s all. We let the universal loader read host_functions.json from host/core/llm.
