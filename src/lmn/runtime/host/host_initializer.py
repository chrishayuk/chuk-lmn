# file: src/lmn/runtime/host/host_initializer.py#
import logging
import wasmtime

# Single universal loader
from lmn.runtime.host.universal_host_loader import UniversalHostLoader

# logger
logger = logging.getLogger(__name__)

def initialize_host_functions(
    linker: wasmtime.Linker,
    store: wasmtime.Store,
    output_list: list,
    memory_ref=None
):
    logger.debug("Initializing host functions via UniversalHostLoader.")
    UniversalHostLoader(linker, store, output_list, memory_ref)
    logger.debug("All host functions initialized.")
