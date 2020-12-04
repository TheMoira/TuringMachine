from turing_utils.scripts.turing_draft import Instruction, InstructionBox
dict1 = {'s_in':'0', 'q_in': 'q0', 's_out':'1', 'q_out':'q1', 'step':'r'}
dict2 = {'s_in':'1', 'q_in': 'q1', 's_out':'0', 'q_out':'q0', 'step':'r'}
dict3 = {'s_in':'0', 'q_in': 'q2', 's_out':'#', 'q_out':'q2', 'step':'l'}

dicts = [dict1, dict2, dict3]

temp = [str(d) for d in dicts]
s = '|'.join(temp)

print(s)
print()
#
# ret = s.split('|')
# instr_list = []
# for instr in ret:
#     dct = eval(instr)
#     keys = tuple(dct)
#     temp = tuple([dct[key] for key in keys])
#     instr_list.append(Instruction(temp))
#
# ibox = InstructionBox(instr_list)
# print(ibox)
    # temp = eval(instr)
    # instr_list += Instruction(temp)

if '|' not in s:
    print("ugh")
else:
    x = s.split('|')
    for instr in x:
        d = eval(instr)
        if type(d) != type(dict):
            print('ughhhh')

