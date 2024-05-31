import json
import sys
from typing import List
from data_path import DataPath
from control_unit import ControlUnit

ASCII_END_OF_LINE_CODE = 10

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
def replace_escape_sequences(input_data: List[str]) -> List[str]:
    
    i = len(input_data) - 1
    while i > 0:
        if input_data[i] == "n" and input_data[i-1] == "\\":
            input_data.pop(i-1)
            input_data[i-1] = ASCII_END_OF_LINE_CODE
            i -= 1  
        i -= 1
    
    return input_data

def main():
    if len(sys.argv) != 3:
        print("Usage: machine.py <asm_file.json> <input_file>")
        sys.exit(1)

    asm_file = sys.argv[1]
    input_file = sys.argv[2]

    asm_data = load_json(asm_file)

    with open(input_file, 'r') as file:
        input_data = replace_escape_sequences(list(file.read().strip()))

    data_path = DataPath(data=asm_data.get('data', []), input_tokens=input_data)

    control_unit = ControlUnit(data_path, asm_data.get('text', []))

    try:
        control_unit.control_logic_procced()
    except StopIteration:
        print("Simulation finished.")
    except EOFError:
        print("End of input reached.")

    # Output the result
    print("Output:\n", "".join(data_path.output_buffer), sep="\n")

if __name__ == "__main__":
    main()