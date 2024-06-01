from __future__ import annotations

import json
import logging
import sys

from control_unit import ControlUnit
from data_path import DataPath

ASCII_END_OF_LINE_CODE = 10


def load_json(filename):
    with open(filename) as file:
        return json.load(file)


def replace_escape_sequences(input_data: list[str]) -> list[str]:
    i = len(input_data) - 1
    while i > 0:
        if input_data[i] == "n" and input_data[i - 1] == "\\":
            input_data.pop(i - 1)
            input_data[i - 1] = ASCII_END_OF_LINE_CODE
            i -= 1
        i -= 1

    return input_data


def main(object_file, input_file):
    asm_data = load_json(object_file)

    with open(input_file) as file:
        input_data = replace_escape_sequences(list(file.read().strip()))

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")

    data_path = DataPath(data=asm_data.get("data", []), input_tokens=input_data)

    control_unit = ControlUnit(data_path, asm_data.get("text", []))

    try:
        control_unit.control_logic_procced()
    except StopIteration:
        pass
    except EOFError:
        pass

    print("".join(data_path.output_buffer), end="")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: machine.py <asm_file.json> <input_file>")
        sys.exit(1)

    object_file = sys.argv[1]
    input_file = sys.argv[2]
    main(object_file, input_file)
