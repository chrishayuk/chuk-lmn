# src/lmn/runtime/universal_host_loader.py

import json
import wasmtime
import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class UniversalHostLoader:
    """
    A single loader that merges all host_functions.json files from
    the various feature folders and registers them in Wasmtime.

    Debug logging is done purely via the logging module. 
    No debug messages go into output_list.
    """

    def __init__(
        self,
        linker: wasmtime.Linker,
        store: wasmtime.Store,
        output_list: list,
        memory_ref=None,
        feature_folders=None
    ):
        # Public references
        self.linker = linker
        self.store = store
        self.output_list = output_list  # used for non-debug or final outputs
        self.memory_ref = memory_ref

        # We'll store function definitions in self.func_defs
        self.func_defs = {}

        # If no folders provided, you can raise an error or specify defaults
        if feature_folders is None:
            feature_folders = [
                "lmn/runtime/host/core/llm",
                "lmn/runtime/host/core/print",
            ]

        logger.debug("UniversalHostLoader initializing with feature folders: %s", feature_folders)

        # Read each folder’s host_functions.json
        for folder in feature_folders:
            json_path = Path(folder) / "host_functions.json"
            if json_path.exists():
                logger.debug("Found host_functions.json in '%s'", folder)
                with json_path.open("r", encoding="utf-8") as f:
                    config = json.load(f)
                    namespace = config.get("namespace", "env")

                    for func_def in config["functions"]:
                        func_name = func_def["name"]
                        # Merge: include 'namespace' and the entire definition
                        self.func_defs[func_name] = {
                            "namespace": namespace,
                            **func_def
                        }
                        logger.debug(
                            "Loaded function '%s' (namespace='%s', handler='%s')",
                            func_name,
                            namespace,
                            func_def.get("handler"),
                        )
            else:
                logger.debug("No host_functions.json found in folder '%s'", folder)

        # Now register everything with Wasmtime
        self.define_host_functions()

    def define_host_functions(self):
        """
        For each function definition, create a Wasmtime function
        that calls our universal dispatcher.
        """
        if not self.func_defs:
            logger.debug("No functions found: self.func_defs is empty.")
            return

        for func_name, def_info in self.func_defs.items():
            name = def_info["name"]
            namespace = def_info["namespace"]
            signature = def_info["signature"]
            handler_str = def_info.get("handler", "<no handler>")

            # Convert JSON signature to Wasmtime FuncType
            param_types = [
                self._map_json_type_to_wasmtime(param["type"])
                for param in signature["parameters"]
            ]
            result_types = [
                self._map_json_type_to_wasmtime(ret["type"])
                for ret in signature["results"]
            ]

            logger.debug(
                "Defining function '%s.%s' -> param_types=%s, result_types=%s, handler=%s",
                namespace, name, param_types, result_types, handler_str
            )

            func_type = wasmtime.FuncType(param_types, result_types)

            def make_wrapper(fn_name):
                def wrapper(*wasm_args):
                    return self._dispatcher(fn_name, *wasm_args)
                return wrapper

            wrapped_func = make_wrapper(name)

            # Register the function
            self.linker.define(
                self.store,
                namespace,
                name,
                wasmtime.Func(self.store, func_type, wrapped_func)
            )

    def _dispatcher(self, func_name: str, *args):
        """
        1) Look up the definition for the given func_name in self.func_defs.
        2) Extract 'handler' from the JSON -> something like "some.module:some_func".
        3) Import that module + function, call it with (def_info, store, memory_ref, output_list, *wasm_args).
        """
        def_info = self.func_defs[func_name]
        handler_str = def_info.get("handler")

        logger.debug(
            "Dispatching function '%s' -> handler='%s', wasm_args=%s",
            func_name, handler_str, args
        )

        if not handler_str:
            raise ValueError(f"No 'handler' found for function '{func_name}'")

        # Expecting "module_path:func_in_module"
        try:
            module_path, func_name_in_module = handler_str.split(":")
        except ValueError:
            raise ValueError(f"handler '{handler_str}' is not in 'module:func' format")

        # Dynamically import the module
        mod = importlib.import_module(module_path)

        # Get the actual function
        if not hasattr(mod, func_name_in_module):
            raise ImportError(
                f"Module '{module_path}' has no attribute '{func_name_in_module}'"
            )
        handler_fn = getattr(mod, func_name_in_module)

        # Invoke the handler
        return handler_fn(def_info, self.store, self.memory_ref, self.output_list, *args)

    def _map_json_type_to_wasmtime(self, t: str) -> wasmtime.ValType:
        """
        Converts JSON types ('i32', 'i64', 'f32', 'f64') to wasmtime.ValType.
        Extend as needed if you have more types.
        """
        if t == "i32":
            return wasmtime.ValType.i32()
        elif t == "i64":
            return wasmtime.ValType.i64()
        elif t == "f32":
            return wasmtime.ValType.f32()
        elif t == "f64":
            return wasmtime.ValType.f64()
        else:
            msg = f"Unsupported type '{t}' in JSON"
            logger.error(msg)
            raise ValueError(msg)
