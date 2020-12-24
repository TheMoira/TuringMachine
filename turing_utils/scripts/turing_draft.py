import random, sys
from io import StringIO

stop = 100

def validate_db_string_to_instr(instr_string):
    pass

def random_example(alphabet, empty_symbol = '#', max_len = 10, min_len = 1):
    length = random.randint(min_len, max_len)
    example = []
    example.append(empty_symbol)
    for _ in range(length):
        example.append(random.choice(alphabet))
    example.append(empty_symbol)
    return example


class Instruction:
    # instruction_tuple examples: (0,q0,0,q0,r)
    def __init__(self, *instruction_tuple):
        self.instr = {'s_in': None, 'q_in': None, 's_out': None, 'q_out': None, 'step': None}
        if len(instruction_tuple) == 1:
            instruction_tuple = instruction_tuple[0]
        elif len(instruction_tuple) < 5:
            print("Wrong values")
            exit()
        iter = 0
        for key in self.instr:
            self.instr[key] = instruction_tuple[iter]
            iter += 1

    def __str__(self):
        return self.instr.__str__()

    def state(self, q_in = False):
        return self.instr['q_out'] if not q_in else self.instr['q_in']

    def value(self, s_in = False):
        return self.instr['s_out'] if not s_in else self.instr['s_in']

    def step(self):
        return 1 if self.instr['step'] == 'r' else -1


class InstructionBox:
    def __init__(self, instructions=None):
        self.instructions = instructions if instructions else []

    def add_instruction(self, instr):
        self.instructions.append(instr)

    def find_instruction(self, s_in, q_in):
        instruction = None
        for instr in self.instructions:
            if instr.state(q_in = True) == q_in and instr.value(s_in = True) == s_in:
                instruction = instr
                break
        return instruction

    def __str__(self):
        # for database
        as_str = [str(d) for d in self.instructions]
        return '|'.join(as_str)

    def from_db_str(self, instr_string):
        instr_dicts = instr_string.split('|')
        for instr in instr_dicts:
            dct = eval(instr)
            keys = tuple(dct)
            temp = tuple([dct[key] for key in keys])
            self.instructions.append(Instruction(temp))


class TuringMachine:
    '''
    start_index - where machine should start in each example, if start_index<0 it will choose place depending on example ength (e.g. last place)
    starting_state - usually 'q0'
    instructions - list of instruction tuples (eg. test_files/input.txt)
    inputs - list of input lists to test machine
    '''
    def __init__(self, start_index, starting_state, instructions, inputs, is_decisive = False):
        if not isinstance(instructions, InstructionBox):
            self.instructions = InstructionBox(instructions)
        else:
            self.instructions = instructions
        self.inputs = inputs
        self.start_index = start_index
        self.starting_state = starting_state
        self.is_decisive = is_decisive

    def add_example(self, example):
        self.inputs.append(example)

    def print(self):
        pass

    def find_instruction(self, s_in, q_in):
        return self.instructions.find_instruction(s_in, q_in)

    def transform_with_instructions(self, count, write_changes):
        ended = False
        example = self.inputs[count]
        print(f'E:{example}')
        index = self.start_index if self.start_index >=0 else len(example) + self.start_index
        current_q = self.starting_state
        current_value = None
        check = 0
        indexes_of_where_the_arrow_is = []
        while not ended and check < stop:
            check += 1
            # assuring the infinity of the tape
            if index <= -1:
                example.insert(0, '#')
                index += 1
            elif index == len(example):
                example.append('#')
            # finding right instruction for the current state and value in example
            current_instruction = self.find_instruction(s_in=example[index], q_in=current_q)
            # if no instruction provided, end functioning of the machine
            if not current_instruction:
                ended = True
            else:
                # update current state
                current_q = current_instruction.state()
                # change the value of currently examined element
                current_value = example[index] = current_instruction.value()
                # let the tape know where to go, depending on step value (L/R)
                indexes_of_where_the_arrow_is.append(index)
                index += current_instruction.step()
                if write_changes:
                    print(example)
        print(f"# {indexes_of_where_the_arrow_is}")
        return current_value


    def start_machine(self, write_changes = True, outfile = None):
        # needed in transform_with_instructions function, which example is examined currently
        count = 0
        original_stdout = sys.stdout
        string_out = StringIO()
        # go through all examples
        for example in self.inputs:
            if outfile:
                sys.stdout = open(outfile, 'w')
            else:
                sys.stdout = string_out
            # print(f"\nExample {count + 1}:")
            # print(example)
            last_value = self.transform_with_instructions(count, write_changes)
            # if is_decisive:
            #     print(f"Outcome: {last_value}")
            count += 1
        sys.stdout = original_stdout
        return string_out, last_value

################################


def line_to_tuple_or_list(string, clear = False, to_list = False):
    if string[-1] == '\n':
        string = string[:-1]
    t = string[1:-1] if not clear else string
    splitter = ',' if not clear else ' '
    data = []
    # for x in t.split(splitter):
    #     if x.isnumeric():
    #         data.append(int(x))
    #     else:
    #         data.append(x)
    for x in t.split(splitter):
        data.append(x)
    if data[-1] == '':
        data = data[:-1]
    return tuple(data) if not to_list else data


def read_instructions_from_file(filename):
    file_opened = False
    instructions = []
    example_inputs = []
    with open(filename, 'r') as f:
        file_opened = True
        is_instruction = False
        is_example = False
        for line in f.readlines():
            if line == "Instructions:\n":
                is_instruction = True
            elif line == "Examples:\n":
                is_example = True
                is_instruction = False
            # elif not line:
            #     instr = False
            elif is_instruction:
                instructions.append(Instruction(line_to_tuple_or_list(line)))
                # print(Instruction(line_to_tuple_or_list(line)))
            elif is_example:
                example_inputs.append(line_to_tuple_or_list(line, True, True))
    if not file_opened:
        print("File cannot be found")
    return instructions, example_inputs

