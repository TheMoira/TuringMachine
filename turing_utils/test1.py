import turing_utils.turing_draft as td
#
def test(filename, start_index, starting_state, is_decisive = False, write_changes = True):
    instructions, ex = td.read_instructions_from_file(filename)
    print(instructions[0])
    print(ex)
    turing = td.TuringMachine(start_index, starting_state, instructions, ex)
    turing.start_machine(is_decisive, write_changes)


if __name__ == '__main__':
    # test('test_files/input.txt', -2, 'q0')
    test('test_files/input_decisive.txt', 1, 'q0', True, False)



# def lol(*tp):
#     print(isinstance(tp,tuple))
#     print(tp)
#
#
# lol(1,2,3)
# lol((1,2,3))
# lol()
