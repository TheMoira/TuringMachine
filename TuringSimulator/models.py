from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from turing_utils.scripts.turing_draft import InstructionBox, Instruction

#
# class Post(models.Model):
#     title = models.CharField(max_length=100)
#     content = models.TextField()
#     # also can use instead of default auto_now=True or auto_now_add=True,
#     # meaning it will change on every post update/only when its created
#     date_posted = models.DateTimeField(default=timezone.now())
#     # relation one:many - on_delete specifies what to do if user is deleted,
#     # (cascade means delete whole post), but doesnt work
#     # both ways - if post is deleted, it wont delete user
#     author = models.ForeignKey(User, on_delete=models.CASCADE)


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


# class InstructionBoxField(models.Field):
#     description = "Class for holding instructions for a specific machine"
#     # potrzebne, zeby przetlumaczyl w metodzie to_python() obiekt nasz customowy
#     __metaclass__ = models.SubfieldBase
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def deconstruct(self):
#         name, path, args, kwargs = super().deconstruct()
#         return name, path, args, kwargs
#
#     def db_type(self, connection):
#         return 'InstructionBox'
#
#     def to_python(self, value):
#         if isinstance(value, InstructionBox):
#             return value
#         if value is None:
#             return value
#         return parse_to_InstructionBox(value)
#
#     def from_db_value(self, value, expression, connection):
#         if value is None:
#             return value
#         return parse_to_InstructionBox(value)
#
#     def get_prep_value(self, value):
#         return parse_to_query(value)
#
#     def value_to_string(self, obj):
#         return parse_to_query(obj)


class TuringMachineDB(models.Model):
    title = models.CharField(max_length=100)
    is_decisive = models.BooleanField(default=False)
    # instructions = InstructionBoxField()
    # has to be specific string
    instructions = models.FileField(upload_to='excel_files', default='excel_files/default_excel.xlsx')
    number_of_states = models.IntegerField()
    alphabet = models.CharField(max_length=100)
    starting_index = models.IntegerField(default=1)
    empty_sign = models.CharField(max_length=1, default='#')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.title


class ExampleDB(models.Model):
    machine = models.ForeignKey(TuringMachineDB, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    example_steps_file = models.FileField(upload_to='text_files', default='text_files/default.txt')

    def __str__(self):
        return self.content
