# src/lmn/runtime/host/host_initializer.py

import wasmtime
import logging
from lmn.runtime.host.core.print.print_functions import PrintHostFunctions
from lmn.runtime.host.core.llm.llm_functions import LLMHostFunctions

# Setup the logger
logger = logging.getLogger(__name__)


def initialize_host_functions(linker: wasmtime.Linker, store: wasmtime.Store, output_list: list, memory_ref=None):
    """
    Initializes and registers all host functions by delegating to individual library modules.

    :param linker: The Wasmtime linker.
    :param store: The Wasmtime store.
    :param output_list: The list to capture output.
    :param memory_ref: Reference to memory, if applicable.
    """
    # Debug
    logger.debug("Initializing host functions.")

    # Instantiate and define PrintHostFunctions
    print_host_functions = PrintHostFunctions(linker, store, output_list, memory_ref)

    # Instantiate and define LLMHostFunctions (our new class)
    llm_host_functions = LLMHostFunctions(linker, store, output_list, memory_ref)

