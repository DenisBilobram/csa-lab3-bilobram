from control_unit import Instruction
from machine import ASCII_END_OF_LINE_CODE
from isa import ArgType

import json
import re
import sys
from typing import Dict, List, Union


def parse_asm(asm_code: str) -> Dict[str, Union[List[int], List[Instruction]]]:
    data_section: List[int] = []
    text_section: List[str] = []
    labels: Dict[str, int] = {}
    address_counter: int = 0

    # Разделение на .data и .text
    sections = re.split(r"\.text", asm_code, flags=re.IGNORECASE)
    if len(sections) != 2:
        raise ValueError("Invalid ASM code format: .text section missing")

    data_code, text_code = sections

    # Обработка .data
    data_lines = data_code.strip().splitlines()
    data_address_counter = 0x0000  # Начальный адрес для секции .data
    for line in data_lines:
        if line.startswith(".data"):
            continue
        label, value = map(str.strip, line.split(":", 1))

        if value.startswith("RESERVE"):
            _, num_bytes = value.split()
            num_bytes = int(num_bytes)
            data_section.extend([0] * num_bytes)
            data_address_counter += num_bytes
        else:
            # Использование регулярного выражения для корректного разделения значений
            value_list = re.findall(r"'[^']*'|\d+", value)

            for literal in value_list:
                if literal.startswith("'") and literal.endswith("'"):
                    char_value = literal.strip("'")
                    if char_value == "\\n":
                        data_section.append(
                            ASCII_END_OF_LINE_CODE
                        )  # ASCII код для переноса строки
                    else:
                        data_section.append(ord(char_value))
                elif literal.isdigit():
                    data_section.append(int(literal))

            data_address_counter += len(value_list)

        labels[label] = data_address_counter - len(value_list)

    # Обработка .text
    text_lines = text_code.strip().splitlines()
    for line in text_lines:
        if ":" in line:
            label, command = map(str.strip, line.split(":", 1))
            labels[label] = address_counter
            if command:
                text_section.append(command)
                address_counter += 1
        else:
            command = line.strip()
            if command:  # добавляем проверку, чтобы пропускать пустые строки
                text_section.append(command)
                address_counter += 1

    # Замена <label> на адреса и формирование инструкций
    resolved_text_section: List[Instruction] = []
    for command in text_section:
        for label, address in labels.items():
            command = re.sub(r"\b" + re.escape(label) + r"\b", str(address), command)
        command = command.replace(",", "")
        parts = command.split()
        if len(parts) == 0:
            continue
        opcode = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        formatted_args: List[ArgType] = []
        for arg in args:
            if re.match(r"^R[0-9]+$", arg):
                formatted_args.append({ArgType.REG.value: arg})
            elif re.match(r"^\d+$", arg):
                formatted_args.append({ArgType.NUMBER.value: arg})
            elif re.match(r"^\(\s*R[0-9]+\s*\)$", arg):
                formatted_args.append({ArgType.INDIRECT_ADDRESS.value: arg.strip("()")})
            elif arg == "'\\n'":
                formatted_args.append(
                    {ArgType.NUMBER.value: str(ASCII_END_OF_LINE_CODE)}
                )

        resolved_text_section.append({"opcode": opcode, "args": formatted_args})

    return {"data": data_section, "text": resolved_text_section}


def translate_to_json(asm_code: str) -> str:
    parsed_asm = parse_asm(asm_code)
    return json.dumps(parsed_asm, indent=4)


def main():
    input_file = sys.argv[1]
    target_file = sys.argv[2]
    with open(input_file, "r", encoding="utf-8") as infile:
        asm_code = infile.read()

    json_output = translate_to_json(asm_code)

    with open(target_file, "w") as outfile:
        outfile.write(json_output)


if __name__ == "__main__":
    main()
