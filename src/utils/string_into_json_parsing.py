import json
from typing import Any, Dict, List


def parse_first_json(message: str) -> Dict[str, Any]:
    start = message.find("{")
    if start == -1:
        raise ValueError("No JSON object found.")
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(message[start:])
    if not isinstance(obj, dict):
        raise ValueError("The first JSON value is not an object.")
    return obj


def parse_first_list(message: str) -> List[Any]:
    start = message.find("[")
    if start == -1:
        raise ValueError("No list found in the input string")
    decoder = json.JSONDecoder()
    parsed_list, end_index = decoder.raw_decode(message[start:])
    if not isinstance(parsed_list, list):
        raise ValueError("First JSON structure found is not a list")
    return parsed_list
