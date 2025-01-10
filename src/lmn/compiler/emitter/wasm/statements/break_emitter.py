# file: lmn/compiler/emitter/wasm/statements/break_emitter.py

import logging

logger = logging.getLogger(__name__)

class BreakEmitter:
    def __init__(self, controller):
        """
        :param controller: Typically the WasmEmitter instance that orchestrates emission.
        """
        self.controller = controller

    def emit_break(self, node, out_lines):
        """
        Emitting a 'BreakStatement' node, e.g.:
            { "type": "BreakStatement" }
        
        We'll do 'br $for_exit' if your for-loops use that label for break.
        """
        logger.debug("BreakEmitter: Emitting break => br $for_exit")
        out_lines.append("  br $for_exit")
