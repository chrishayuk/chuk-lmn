# file: src/lmn/runtime/host/core/tools/handler.py

import json
import logging
import requests
import time

from lmn.runtime.host.core.malloc.call_malloc import store_string_with_malloc

# logger
logger = logging.getLogger(__name__)

def get_internet_time(def_info, store, memory_ref, output_list, *args) -> int:
    """
    Fetch the entire JSON from "http://worldtimeapi.org/api/timezone/Etc/UTC"
    and return it as a pointer to text in WASM memory.
    LMN sees it as a string => 'string'.
    """
    func_name = def_info["name"]
    logger.debug(f"[{func_name}] Called with {args=}")

    if not memory_ref or memory_ref[0] is None:
        logger.debug(f"[{func_name}] memory_ref invalid => returning 0.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]

    # The API endpoint
    url = "http://worldtimeapi.org/api/timezone/Etc/UTC"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()  # Python dict
        # Convert to JSON text
        json_str = json.dumps(data, ensure_ascii=False)

        # Store it in WASM memory => return pointer
        ptr = store_string_with_malloc(store, mem, output_list, json_str)
        return ptr

    except Exception as e:
        logger.debug(f"[{func_name}] Error: {e}")
        output_list.append(f"<get_internet_time error: {e}>")
        return 0

def get_system_time(def_info, store, memory_ref, output_list, *args) -> int:
    """
    Returns the local system time as an integer (UNIX timestamp).
    """
    func_name = def_info["name"]
    logger.debug(f"[{func_name}] Called with {args=}")

    if not memory_ref or memory_ref[0] is None:
        logger.debug(f"[{func_name}] memory_ref invalid => returning 0.")
        output_list.append("<no memory>")
        return 0

    now = int(time.time())
    logger.debug(f"[{func_name}] system_time={now}")
    return now

def get_weather(def_info, store, memory_ref, output_list, *args) -> int:
    """
    Calls open-meteo => returns pointer to the JSON text in WASM memory.
    We'll parse the response as Python JSON, optionally tweak it,
    then do json.dumps(...) to produce a final string.
    """
    func_name = def_info["name"]
    logger.debug(f"[{func_name}] Called with {args=}")

    # 0) Basic validation
    if not memory_ref or memory_ref[0] is None:
        logger.debug(f"[{func_name}] memory_ref invalid => returning 0.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]

    # 1) Parse lat/lon from args if provided
    lat, lon = 35.0, 139.0
    if len(args) >= 2:
        lat = float(args[0])
        lon = float(args[1])

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m"
    logger.debug(f"[{func_name}] => requesting {url}")

    try:
        # 2) Fetch data
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        # 3) Convert the response to a Python dict
        data = resp.json()   # parse JSON => dict

        # 4) (Optional) Tweak or add a new key
        data["fetched_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 5) Dump back to JSON string
        data_json = json.dumps(data, ensure_ascii=False)

        logger.debug(f"[{func_name}] => final JSON length={len(data_json)}")

        # 6) Store it in WASM memory => pointer
        ptr = store_string_with_malloc(store, mem, output_list, data_json)
        return ptr

    except Exception as e:
        logger.debug(f"[{func_name}] Error: {e}")
        output_list.append(f"<get_weather_openmeteo error: {e}>")
        return 0

def get_joke(def_info, store, memory_ref, output_list, *args) -> int:
    """
    Grab a joke from https://icanhazdadjoke.com => store in WASM memory => return pointer
    """
    func_name = def_info["name"]
    logger.debug(f"[{func_name}] Called with {args=}")

    if not memory_ref or memory_ref[0] is None:
        logger.debug(f"[{func_name}] memory_ref invalid => returning 0.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]

    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": "text/plain"}

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        joke_text = resp.text.strip()
        logger.debug(f"[{func_name}] => fetched joke: {joke_text[:50]}...")

        # Key fix: pass all four parameters
        return store_string_with_malloc(store, mem, output_list, joke_text)

    except Exception as e:
        logger.debug(f"[{func_name}] Error: {e}")
        output_list.append(f"<get_joke_service error: {e}>")
        return 0
