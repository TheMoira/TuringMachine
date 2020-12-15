import turing_utils.scripts.turing_draft as turing
import turing_utils.scripts.excel_utils as exl
import turing_utils.scripts.using_machine as use_test
import time
import os.path
from pathlib import Path

if __name__ == '__main__':
    menu = """
    c - create new machine
    u - use existing machine
    r - read existing machine from file
    """
    mode = input('What do you want to do?' + menu)

    if mode == 'c':
        alphabet_raw = input("Insert alphabet\nFormat example: a,b,c,d,#\n")
        number_of_states = int(input("Insert number of states (without ending state): "))
        name = input("Insert machine name: ")
        alphabet_raw = alphabet_raw.replace(' ', '')
        alphabet = alphabet_raw.split(',')
        prep_file = exl.generate_xlsx_file(name, alphabet, number_of_states, path='../test_files/input/excel_inputs/')
        print(f"Fill the file {prep_file} with proper instructions for {name} turing machine")
    elif mode == 'u':
        file_path = input("Insert path to excel filled file: ")
        if not os.path.isfile(file_path):
            print(f"No file {file_path}")
            exit()
        out_file_path = input("Insert path to outfile: ")
        if not os.path.isfile(out_file_path):
            print(f"No file {out_file_path}")
            exit()
        final_file = input("Insert path to ultimate file: ")
        if not os.path.isfile(final_file):
            print(f"No file {final_file}")
            exit()
        example = input("Insert example to execute (format: #abc#): ")
        is_dec = input("Is it a decisive machine? (y/n) ")
        starting_index = int(input("Insert index of where machine should start (-1 if on last element): "))
        is_dec = True if is_dec == 'y' else False
        examples = [example.split()]
        print(examples)
        exl.generate_instructions_from_xlsx_file(file_path, True, out_file_path, examples)
        time.sleep(3)
        use_test.machine_use_testing(out_file_path, starting_index, 'q0', is_dec, True, final_file)
    elif mode == 'r':
        file_path = input("Insert path to file with paths: ")
        if not Path(file_path).exists():
            print(f"No file {file_path}")
            exit()
        files = []
        examples = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i in range(3):
                line = lines[i][:-1]
                files.append(line)
                if i == 0 and not Path(line).exists():
                    print(f"No file {line}")
                    exit()
            ex_line = list(lines[3][:-1])
            print(ex_line)
            examples.append(ex_line)
            is_dec = True if lines[4][0] == 'y' else False
            index = int(lines[5])
            exl.generate_instructions_from_xlsx_file(files[0], True, files[1], examples)
            while not os.path.exists(files[1]):
                time.sleep(1)
            use_test.machine_use_testing(files[1], index, 'q0', is_dec, True, files[2])
    else:
        print("Not an option")