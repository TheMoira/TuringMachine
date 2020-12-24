import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    # valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls']
    valid_extensions = ['.xlsx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def validate_example_with_alphabet(example, alphabet):
    for letter in list(example):
        if letter not in list(alphabet):
            return False
    return True


def validate_example_excel_filled_out(machine):
    print(f'validator: id={machine.id} excel_empty={machine.excel_empty}')
    return not machine.excel_empty