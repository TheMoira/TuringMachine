from django.db import models
from django.contrib.auth.models import User
from turing_utils.scripts.turing_draft import InstructionBox, Instruction, TuringMachine
from .validators import validate_file_extension
from django.urls import reverse
from turing_utils.scripts.excel_utils import generate_xlsx_file, generate_instructions_from_xlsx_file
from Django_project.settings import MEDIA_ROOT
from django.core.exceptions import ValidationError
from openpyxl import Workbook


def parse_to_InstructionBox(value):
    instructions = value.split('|')
    instr_list = []
    for instr in instructions:
        dct = eval(instr)
        keys = tuple(dct)
        instr_tuple = tuple([dct[key] for key in keys])
        instr_list.append(Instruction(instr_tuple))
    return InstructionBox(instr_list)


def parse_to_query(obj):
    # {'s_in': a, 'q_in': b, 's_out': c, 'q_out': d, 'step': e}|{'s_in': ...
    return str(obj)




# TODO: dodac w initach wywolanie funkcji do zrobienia co trzeba (kroki instrukcji itd)
class TuringMachineDB(models.Model):
    title = models.CharField(max_length=100)
    is_decisive = models.BooleanField(default=False)
    # has to be specific string
    instructions = models.FileField(upload_to='excel_files', default='excel_files/default_excel.xlsx', validators=[validate_file_extension])
    number_of_states = models.IntegerField()
    alphabet = models.CharField(max_length=100)
    starting_index = models.IntegerField(default=1)
    empty_sign = models.CharField(max_length=1, default='#')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    initial_number_of_states = models.IntegerField(default=0)
    initial_alphabet = models.CharField(max_length=100, default='')
    excel_empty = True


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('machine-detail', kwargs={'pk': self.pk})

    def prepare_excel(self):
        name = str(self.title)
        alphabet = str(self.alphabet).split(',')
        number_of_states = int(self.number_of_states)
        empty_mark = str(self.empty_sign)
        path = self.instructions.path
        workbook = generate_xlsx_file(name, alphabet, number_of_states, path, empty_mark, return_only_workbook=True)
        filepath = MEDIA_ROOT + f"/excel_files/{name}_{self.author}.xlsx"
        workbook.save(filepath)
        self.instructions = filepath
        self.excel_empty = True
        # elif self.excel_filled:
        #     outputpath = MEDIA_ROOT + f"/excel_files/{name}_{self.author}.xlsx"
        #     generate_instructions_from_xlsx_file(self.instructions.path, True, files[1], examples)


# TODO: ogarnac unique - zrezygnowac albo jakos ulepszyc
class ExampleDB(models.Model):
    machine = models.ForeignKey(TuringMachineDB, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=50, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    example_steps = models.TextField(default='')

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('machine-detail', kwargs={'pk': self.machine_id})

    # def clean(self):
    #     # Don't allow duplicates
    #     existing_examples = ExampleDB.objects.filter(machine=self.machine)
    #     for example in existing_examples:
    #         if self.content == example.content:
    #             raise ValidationError({'content':f'Example {self.content} already exists for this machine'})

    def format_content(self):
        list_content = list(str(self.content))
        empty_sign = str(self.machine.empty_sign)
        if list_content[0] != empty_sign:
            list_content.insert(0,'#')
        if list_content[-1] != empty_sign:
            list_content.append('#')
        return list_content

    def prepare_steps_text(self):
        instructions = generate_instructions_from_xlsx_file(filename=str(self.machine.instructions.path))
        print(str(self.machine.instructions.path))
        for i in instructions:
            print(str(i))
        examples = []
        examples.append(self.format_content())
        machine_obj = TuringMachine(int(self.machine.starting_index), 'q0', instructions, examples)
        output = machine_obj.start_machine(self.machine.is_decisive)
        self.example_steps = output.getvalue()
        print(self.example_steps)


