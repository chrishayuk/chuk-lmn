# src/lmn/cli/run_wasm.py
from lmn.runtime.wasm_runner import run_wasm, create_environment

if __name__ == "__main__":
    # Reusable environment
    env = create_environment()

    # Example runs
    print(run_wasm("your LMN code here", env=env))
    print(run_wasm("additional LMN code", env=env))