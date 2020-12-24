# import turing_utils.turing_draft as td
import turing_utils.scripts.turing_draft as td

def machine_use_testing(filename, start_index, starting_state, is_decisive = False, write_changes = False, outfile = None):
    instructions, ex = td.read_instructions_from_file(filename)
    print(instructions[0])
    print(ex)
    turing = td.TuringMachine(start_index, starting_state, instructions, ex, is_decisive=is_decisive)
    turing.start_machine(write_changes, outfile)


# if __name__ == '__main__':
    # test('test_files/input.txt', -2, 'q0', True, True, 'out4.txt')
    # test('test_files/input_decisive.txt', 1, 'q0', True, True, 'out5.txt')
    # test('test_files/input_2.txt', 1, 'q0', False, True, 'out3.txt')

# def lol(*tp):
#     print(isinstance(tp,tuple))
#     print(tp)
#
#
# lol(1,2,3)
# lol((1,2,3))
# lol()
