from django.db import models
import os
from django.utils import timezone
from django.contrib.auth.models import User
from turing_utils.scripts.turing_draft import InstructionBox, Instruction
from .validators import validate_file_extension
from django.urls import reverse
from turing_utils.scripts.excel_utils import generate_xlsx_file, generate_instructions_from_xlsx_file
from Django_project.settings import MEDIA_ROOT
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
    # instructions = InstructionBoxField()
    # has to be specific string
    instructions = models.FileField(upload_to='excel_files', default='excel_files/default_excel.xlsx', validators=[validate_file_extension])
    number_of_states = models.IntegerField()
    alphabet = models.CharField(max_length=100)
    starting_index = models.IntegerField(default=1)
    empty_sign = models.CharField(max_length=1, default='#')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    needed_empty_excel = True
    excel_filled = False

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('machine-detail', kwargs={'pk': self.pk})

    def prepare_excel(self):
        if self.needed_empty_excel:
            name = str(self.title)
            alphabet = str(self.alphabet).split(',')
            number_of_states = int(self.number_of_states)
            empty_mark = str(self.empty_sign)
            path = self.instructions.path
            workbook = generate_xlsx_file(name, alphabet, number_of_states, path, empty_mark, return_only_name=True)
            filepath = MEDIA_ROOT + f"/excel_files/{name}_{self.author}.xlsx"
            workbook.save(filepath)
            self.instructions = filepath
            self.needed_empty_excel = False
        # elif self.excel_filled:
        #     outputpath = MEDIA_ROOT + f"/excel_files/{name}_{self.author}.xlsx"
        #     generate_instructions_from_xlsx_file(self.instructions.path, True, files[1], examples)


class ExampleDB(models.Model):
    machine = models.ForeignKey(TuringMachineDB, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    example_steps_file = models.FileField(upload_to='text_files', default='text_files/default.txt')

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('machine-detail', kwargs={'pk': self.machine_id})
