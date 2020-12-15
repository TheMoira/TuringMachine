from django.forms.models import ModelForm
from django.forms.fields import FileField
from django.db.models import Q
from .models import TuringMachineDB, ExampleDB
from django.forms import Form, FileField


class ExampleForm(ModelForm):
    class Meta:
        model = ExampleDB
        fields = ['machine', 'content']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        user = self.request.user
        self.m_id = kwargs.pop('m_id')
        super(ExampleForm, self).__init__(*args, **kwargs)
        self.fields['machine'].queryset = TuringMachineDB.objects.filter(Q(author=user) | Q(author=1))
        # self.fields['machine'] = TuringMachineDB.objects.filter(id=self.m_id).first()


class UploadFileForm(Form):
    file = FileField()

# class UploadFileForm(ModelForm):
#     class Meta:
#         model = TuringMachineDB
#         fields = ('instructions')