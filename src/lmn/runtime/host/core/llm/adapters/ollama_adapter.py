# src/lmn/runtime/core/llm/adapters/ollama_adapter.py

from ollama import chat, ChatResponse

class OllamaAdapter:
    """
    A thin wrapper around Ollama's Python API.
    """

    def __init__(self, output_list):
        self.output_list = output_list

    def chat(self, model_name: str, messages: list[dict]) -> str:
        """
        Calls Ollama with the provided model name and a list of message dicts,
        returning the LLM's response as a string.

        Example messages:
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": "Why is the sky blue?"}
            ]
        """
        try:
            response: ChatResponse = chat(
                model=model_name,
                messages=messages
            )
            return response.message.content
        except Exception as e:
            self.output_list.append(f"[LLM] Ollama call failed: {e}")
            return "LLM error."
