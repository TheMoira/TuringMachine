from django.db import models
from django.contrib.auth.models import User
from turing_utils.scripts.turing_draft import InstructionBox, Instruction, TuringMachine
from .validators import validate_file_extension
from django.urls import reverse
from turing_utils.scripts.excel_utils import generate_xlsx_file, generate_instructions_from_xlsx_file
from Django_project.settings import MEDIA_ROOT, DEFAULT_FILE_STORAGE, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_DEFAULT_ACL, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION_NAME
from django.db.models import Q
from tempfile import NamedTemporaryFile
import boto3
from openpyxl import Workbook, styles as ops, load_workbook


s3 = boto3.resource('s3')

FILES_PATH = 'excel_files/'
# DEFAULT_EXCEL_FILE_PATH = FILES_PATH + 'default_excel.xlsx'
AWS_EXCEL_FILE_PATH = 'https://turing-machine-files-bucket.s3.us-east-2.amazonaws.com/excel_files/'
DEFAULT_EXCEL_FILE_PATH = AWS_EXCEL_FILE_PATH + 'default_excel.xlsx'


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


def validate_example_avoid_duplicates(example_cont, user_id, machine_id):
    existing_examples = ExampleDB.objects.filter(Q(Q(author_id=user_id) | Q(author_id=1)) & Q(machine_id=machine_id))
    for ex in existing_examples:
        if example_cont == ex.content:
            return False
    return True


class TuringMachineDB(models.Model):
    title = models.CharField(max_length=100)
    is_decisive = models.BooleanField(default=False)
    # has to be specific string
    instructions = models.FileField(upload_to='excel_files', default=DEFAULT_EXCEL_FILE_PATH, validators=[validate_file_extension])
    number_of_states = models.IntegerField()
    alphabet = models.CharField(max_length=100)
    starting_index = models.IntegerField(default=1)
    empty_sign = models.CharField(max_length=1, default='#')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    initial_number_of_states = models.IntegerField(default=0)
    initial_alphabet = models.CharField(max_length=100, default='')
    excel_empty = models.BooleanField(default=True)
    aws_file_key = models.CharField(max_length=100, default='')
    aws_file_path = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('machine-detail', kwargs={'pk': self.pk})

    def prepare_excel(self):
        print(self.instructions)
        # name = str(self.title)
        # alphabet = str(self.alphabet).split(',')
        # number_of_states = int(self.number_of_states)
        # empty_mark = str(self.empty_sign)
        # path = ''
        # workbook = generate_xlsx_file(name, alphabet, number_of_states, path, empty_mark, return_only_workbook=True)
        # # filepath = MEDIA_ROOT + f"/excel_files/{name}_{self.author}.xlsx"
        # # filepath = AWS_EXCEL_FILE_PATH + f"{name}_{self.author}.xlsx"
        # # filepath = f'excel_files/{name}_{self.author}.xlsx'
        # with NamedTemporaryFile() as temp:
        #     workbook.save(temp.name)
        #     print(temp.name)
        #     self.aws_file_key = FILES_PATH + f'{name}_{self.author}.xlsx'
        #     self.aws_file_path = AWS_EXCEL_FILE_PATH + f'{name}_{self.author}.xlsx'
        #     s3.meta.client.upload_file(temp.name, AWS_STORAGE_BUCKET_NAME, self.aws_file_key)
        # elif self.excel_filled:
        #     outputpath = MEDIA_ROOT + f"/excel_files/{name}_{self.author}.xlsx"
        #     generate_instructions_from_xlsx_file(self.instructions.path, True, files[1], examples)



class ExampleDB(models.Model):
    machine = models.ForeignKey(TuringMachineDB, on_delete=models.CASCADE)
    content = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    example_steps = models.TextField(default='None')
    last_value = models.CharField(default='None', max_length=5)

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('machine-detail', kwargs={'pk': self.machine_id})

    def format_content(self):
        list_content = list(str(self.content))
        empty_sign = str(self.machine.empty_sign)
        if list_content[0] != empty_sign:
            list_content.insert(0,'#')
        if list_content[-1] != empty_sign:
            list_content.append('#')
        return list_content

    def prepare_steps_text(self):
        workbook = load_workbook(self.machine.instructions)
        instructions = generate_instructions_from_xlsx_file(filename='', ready_workbook=workbook)
        # print(str(self.machine.instructions.path))
        # for i in instructions:
        #     print(str(i))
        examples = []
        examples.append(self.format_content())
        machine_obj = TuringMachine(int(self.machine.starting_index), 'q0', instructions, examples, is_decisive=self.machine.is_decisive)
        output, last_value = machine_obj.start_machine()
        self.example_steps = output.getvalue()
        if self.machine.is_decisive:
            self.last_value = str(last_value)
        # print(self.example_steps)


