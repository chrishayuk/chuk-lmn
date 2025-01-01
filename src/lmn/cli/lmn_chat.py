#!/usr/bin/env python3
# file: src/lmn/cli/lmn_chat.py
import logging
import colorama
from colorama import Fore, Style
from ollama import chat, ChatResponse

# Import cli modules
from lmn.cli.utils.banner import get_ascii_banner
from lmn.cli.utils.system_prompt import get_system_prompt

# Import lmn modules
from lmn.runtime.wasm_runner import run_wasm, create_environment
from lmn.runtime.utils import extract_lmn_code

# Initialize environment for the chat session
env = create_environment()

# setup logging
logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s"
)

def main():
    # setup colorama
    colorama.init(autoreset=True)

    # setup the ascii banner
    ascii_banner = get_ascii_banner()
    print(ascii_banner)
    print(f"LMN Language Chat Playground  {Fore.WHITE}v0.0.1 (2024-12-30){Style.RESET_ALL}")
    print("Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")

    # Grab the system prompt from our new module
    system_prompt = get_system_prompt()

    # setup the conversation history
    conversation = [{"role": "system", "content": system_prompt}]

    # loop until the user quits
    while True:
        try:
            # user input prompt
            user_input = input(f"{Fore.CYAN}You> {Style.RESET_ALL}")
        except EOFError:
            # error
            print(f"\n{Fore.CYAN}Exiting LMN Chat. Goodbye!{Style.RESET_ALL}")
            break

        # quit or exit
        if user_input.strip().lower() in ("quit", "exit"):
            # quit or exit
            print(f"{Fore.CYAN}Exiting LMN Chat. Goodbye!{Style.RESET_ALL}")
            break

        # help
        if user_input.strip() == "?":
            # show help
            show_help()
            continue

        # 1) Add user's message
        conversation.append({"role": "user", "content": user_input})

        # 2) Call Ollama
        response_text = do_llama_chat(conversation)

        # 3) Print LLM's raw reply
        print(f"{Fore.MAGENTA}LLM> {Style.RESET_ALL}{response_text}")

        # 4) Extract LMN code blocks
        blocks = extract_lmn_code(response_text)

        # check if blocks
        if blocks:
            # print some debug to show we've executred the code
            print(f"{Fore.YELLOW}[Detected {len(blocks)} LMN code block(s). Running...]{Style.RESET_ALL}")

            # for each detected code block
            for block in blocks:
                # run the was
                outputs = run_wasm(block, env=env)

                # print the outputs
                for line in outputs:
                    # print the output
                    print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")

        # 5) Add LLM response to conversation
        conversation.append({"role": "assistant", "content": response_text})

def do_llama_chat(conversation) -> str:
    try:
        # setup the response
        response: ChatResponse = chat(
            model='llama3.2',
            messages=conversation,
        )

        # return the content
        return response.message.content
    except Exception as e:
        # error
        return f"(Error during LLM call: {e})"

def show_help():
    # show help
    print(f"{Fore.GREEN}\nLMN Chat Help{Style.RESET_ALL}")
    print(" - Type questions or instructions. If code is requested, LLM may produce LMN code.")
    print(" - Code in ```lmn ...``` blocks is automatically compiled & run.")
    print(" - 'quit' or 'exit' ends this session.\n")

if __name__ == "__main__":
    # call main
    main()
