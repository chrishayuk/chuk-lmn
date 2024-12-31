# file: src/lmn/cli/utils/banner.py

from colorama import Fore, Style

def get_ascii_banner() -> str:
    """
    Returns the ASCII banner for LMN Language Chat Playground.
    """
    return f"""{Fore.GREEN}
oo______ooo_____ooo_ooo____oo_
oo______oooo___oooo_oooo___oo_
oo______oo_oo_oo_oo_oo_oo__oo_
oo______oo__ooo__oo_oo__oo_oo_
oo______oo_______oo_oo___oooo_
ooooooo_oo_______oo_oo____ooo_
______________________________
{Style.RESET_ALL}
"""
