# file: lmn/runtime/universal_host_loader.py

import wasmtime
import importlib
import logging
from lmn.builtins import BUILTINS  # The merged dictionary from lmn/builtins/__init__.py

logger = logging.getLogger(__name__)

class UniversalHostLoader:
    """
    A single loader that takes all definitions from `lmn.builtins.BUILTINS`
    and registers them in Wasmtime.
    """

    def __init__(
        self,
        linker: wasmtime.Linker,
        store: wasmtime.Store,
        output_list: list,
        memory_ref=None
    ):
        self.linker = linker
        self.store = store
        self.output_list = output_list
        self.memory_ref = memory_ref

        # We'll store function definitions in self.func_defs:
        #  { "funcName": { "name": "...", "namespace": "...", "signature": {...}, "handler": "...", ... }, ... }
        self.func_defs = {}

        # 1) Merge all built-ins from `BUILTINS` into `self.func_defs`
        self._merge_builtins(BUILTINS)

        # 2) Register everything with Wasmtime
        self.define_host_functions()

    def define_host_functions(self):
        """
        Convert each entry in self.func_defs into a Wasmtime function
        and register it with the linker.
        """
        if not self.func_defs:
            logger.debug("No functions found in BUILTINS.")
            return

        for func_name, def_info in self.func_defs.items():
            name = def_info["name"]
            namespace = def_info.get("namespace", "env")  # fallback to "env"
            signature = def_info["signature"]
            handler_str = def_info.get("handler")

            # Convert signature (JSON-like) to Wasmtime FuncType
            param_types = [
                self._map_json_type_to_wasmtime(param["type"])
                for param in signature.get("parameters", [])
            ]
            result_types = [
                self._map_json_type_to_wasmtime(ret["type"])
                for ret in signature.get("results", [])
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

            # Register the function in Wasmtime
            self.linker.define(
                self.store,
                namespace,
                name,
                wasmtime.Func(self.store, func_type, wrapped_func)
            )

    def _dispatcher(self, func_name: str, *args):
        """
        Look up the definition for `func_name` in self.func_defs,
        parse the handler string, import the module, call the handler.
        """
        def_info = self.func_defs[func_name]
        handler_str = def_info.get("handler")

        logger.debug("Dispatching '%s' -> handler='%s', wasm_args=%s",
                     func_name, handler_str, args)

        if not handler_str:
            raise ValueError(f"No 'handler' found for function '{func_name}'")

        # Expect "module_path:func_in_module"
        module_path, func_name_in_module = handler_str.split(":")

        mod = importlib.import_module(module_path)
        handler_fn = getattr(mod, func_name_in_module, None)
        if not handler_fn:
            raise ImportError(
                f"Module '{module_path}' has no attribute '{func_name_in_module}'"
            )

        # Call the handler with (def_info, store, memory_ref, output_list, *args)
        return handler_fn(def_info, self.store, self.memory_ref, self.output_list, *args)

    def _merge_builtins(self, builtins_dict: dict):
        """
        Convert the loaded BUILTINS dictionary into `self.func_defs` shape.
        
        We assume each key in BUILTINS is the function name, and the value
        is a dict with at least { "name", "namespace", "signature", "handler", ... }.
        """
        for fn_name, fn_info in builtins_dict.items():
            # Ensure the "name" field is set if missing
            if "name" not in fn_info:
                fn_info["name"] = fn_name

            # Store it in self.func_defs
            self.func_defs[fn_name] = fn_info

    def _map_json_type_to_wasmtime(self, t: str) -> wasmtime.ValType:
        """
        Convert JSON string types ('i32', 'i64', 'f32', 'f64') to wasmtime.ValType.
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
            msg = f"Unsupported type '{t}' in built-ins"
            logger.error(msg)
            raise ValueError(msg)
