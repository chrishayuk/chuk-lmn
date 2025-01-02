# src/lmn/runtime/core/print/print_functions.py
import wasmtime
from pathlib import Path

# Import your universal loader
from lmn.runtime.host.universal_host_loader import UniversalHostLoader

class PrintHostFunctions:
    def __init__(self, linker: wasmtime.Linker, store: wasmtime.Store, output_list: list, memory_ref=None):
        """
        Initializes and registers print-related host functions.
        
        :param linker:      The Wasmtime linker.
        :param store:       The Wasmtime store.
        :param output_list: The list to capture output/logs.
        :param memory_ref:  Reference to memory, if applicable.
        """
        # 1) Just let the universal loader do all the heavy lifting.
        #    For example, we can tell it to read host_functions.json from the print folder.
        feature_folder = Path("src/lmn/runtime/host/core/print")

        # 2) If you have a single universal loader for the entire app, 
        #    you could instantiate it once. 
        #    But if we only want to load the print JSON here, we can do something like:
        universal_loader = UniversalHostLoader(
            linker=linker, 
            store=store, 
            output_list=output_list, 
            memory_ref=memory_ref,
            feature_folders=[feature_folder]
        )
