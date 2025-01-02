# src/lmn/runtime/core/llm/adapters/lm_adapter.py

from lmn.runtime.host.core.llm.adapters.ollama_adapter import OllamaAdapter

class LLMAdapter:
    """
    Top-level adapter that dispatches to specific LLM providers.
    Default provider is 'ollama' if not specified.
    """

    def __init__(self, output_list):
        self.output_list = output_list
        # Instantiate each provider adapter here
        self.ollama_adapter = OllamaAdapter(output_list)
        # Future adapters (OpenAI, Azure, etc.) can be added similarly.

    def chat(self, provider: str, model_name: str, messages: list[dict]) -> str:
        """
        Dispatches to the appropriate adapter based on 'provider'.

        :param provider:    Name of the provider, e.g. 'ollama'
        :param model_name:  The model to use, e.g. 'llama3.2'
        :param messages:    A list of messages, each a dict like:
                            {
                                "role": "user",
                                "content": "Hello, how are you?"
                            }
        :return: The LLM's response text.
        """
        provider_lower = (provider or "").strip().lower()

        # Default to Ollama if missing/empty/unrecognized
        if provider_lower in ("", "ollama"):
            return self.ollama_adapter.chat(model_name, messages)
        else:
            # In a real implementation, you'd route to other adapters or raise an error.
            self.output_list.append(
                f"[LLM] Unknown provider '{provider}', falling back to Ollama."
            )
            return self.ollama_adapter.chat(model_name, messages)
