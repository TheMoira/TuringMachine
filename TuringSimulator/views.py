from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import TuringMachineDB, ExampleDB, DEFAULT_EXCEL_FILE_PATH, validate_example_avoid_duplicates
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadFileForm
from django.templatetags.static import static
from .validators import validate_example_excel_filled_out, validate_example_with_alphabet
from tempfile import NamedTemporaryFile
import boto3
import botocore
from Django_project.settings import AWS_STORAGE_BUCKET_NAME
from openpyxl.writer.excel import save_virtual_workbook
from turing_utils.scripts.excel_utils import generate_xlsx_file, generate_instructions_from_xlsx_file

s3 = boto3.resource('s3')


# main page
def index(request):
    # return HttpResponse("<h1>Turing Machine Simulator</h1>")
    return render(request, 'TuringSimulator/index.html')


def machine_list(request):
    machines = TuringMachineDB.objects.all()
    context = { 'machines': machines, }
    return render(request, 'TuringSimulator/machines.html', context)


# about page
def about(request):
    return render(request, 'TuringSimulator/about.html')


def stylesheet(request):
    return render(request, '../static/TuringSimulator/main.css')


def stylesheet_sim(request):
    return render(request, '../static/TuringSimulator/main2.css')


def simulation(request, pk):
    example = get_object_or_404(ExampleDB, pk=pk)
    machine_id = example.machine_id
    lines = example.example_steps
    scratched = static('TuringSimulator/resources/Scratched.png')
    metal = static('TuringSimulator/resources/metal_texture.jpg')
    last_value = example.last_value
    context = {
        'lines': lines,
        'scratched': scratched,
        'metal':metal,
        'machine_id':machine_id,
        'last_value':last_value,
    }
    return render(request, 'TuringSimulator/simulation.html', context)


# def download_instruction(request, object_id):
#     machine = get_object_or_404(TuringMachineDB, pk=object_id)
#     file = machine.instructions
#     path = machine.instructions.path
#     response = HttpResponse(file.read(), content_type="application/vnd.ms-excel")
#     response['Content-Disposition'] = 'attachment; filename=' + path
#     return response

# def download_instruction(request, object_id):
#     machine = get_object_or_404(TuringMachineDB, pk=object_id)
#     key = machine.aws_file_key
#     bucket = AWS_STORAGE_BUCKET_NAME
#     try:
#         file = NamedTemporaryFile(suffix = '.xlsx', delete=False)
#         s3.Bucket(bucket).download_file(key, file.name)
#         response = HttpResponse(file.read(), content_type="application/vnd.ms-excel")
#         response['Content-Disposition'] = 'attachment; filename=' + file.name
#         return response
#     except botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             return None
#         else:
#             raise
#     else:
#         raise

def download_instruction(request, object_id):
    # machine = get_object_or_404(TuringMachineDB, pk=object_id)
    # filename = machine.aws_file_path
    # response = HttpResponse(content_type='application/force-download')
    # response['Content-Disposition'] = 'attachment;filename="%s"' % filename
    # response["X-Sendfile"] = filename
    # return response
    machine = get_object_or_404(TuringMachineDB, pk=object_id)
    name = str(machine.title)
    alphabet = str(machine.alphabet).split(',')
    number_of_states = int(machine.number_of_states)
    empty_mark = str(machine.empty_sign)
    if machine.excel_empty:
        print('Machine: not filled')
        path = ''
        workbook = generate_xlsx_file(name, alphabet, number_of_states, path, empty_mark, return_only_workbook=True)
        response = HttpResponse(save_virtual_workbook(workbook), content_type='application/vnd.ms-excel')
    else:
        file = machine.instructions
        response = HttpResponse(file.read(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment;filename=' + f'{name}_{machine.author}.xlsx'
    response["X-Sendfile"] = f'{name}_{machine.author}.xlsx'
    return response


def upload_instruction(request, object_id):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            machine = get_object_or_404(TuringMachineDB, pk=object_id)
            machine.instructions = file
            machine.excel_empty = False
            machine.save()
            current_examples = ExampleDB.objects.filter(machine_id=object_id)
            for example in current_examples:
                example.prepare_steps_text()
            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
    else:
        form = UploadFileForm()
    return render(request, 'TuringSimulator/UploadInstr.html', {'form': form})


class MachineListView(ListView):
    model = TuringMachineDB
    template_name = 'TuringSimulator/machines.html'
    context_object_name = 'machines'
    ordering = ['title']


class MachineDetailView(DetailView):
    model = TuringMachineDB


class ExampleCreateView(LoginRequiredMixin, CreateView):
    model = ExampleDB
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.machine = self.t_machine
        content = self.request.POST.get('content')
        if not validate_example_with_alphabet(content, self.t_machine.alphabet):
            form.add_error(None, 'Not compatible with machine alphabet')
            return super().form_invalid(form)
        if not validate_example_avoid_duplicates(content, self.request.user.id, self.t_machine.id):
            form.add_error(None, 'This example already exists for the machine')
            return super().form_invalid(form)
        if not validate_example_excel_filled_out(self.t_machine):
            form.add_error(None, 'Cannot create example for a machine with default instructions file')
            return super().form_invalid(form)
        form.instance.prepare_steps_text()
        form.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.t_machine = get_object_or_404(TuringMachineDB, pk=kwargs['machineId'])
        return super().dispatch(request, *args, **kwargs)



class MachineCreateView(LoginRequiredMixin, CreateView):
    model = TuringMachineDB
    fields = ['title', 'is_decisive', 'number_of_states', 'alphabet', 'starting_index', 'empty_sign']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        form.instance.prepare_excel()
        form.instance.initial_alphabet = form.instance.alphabet
        form.instance.initial_number_of_states = form.instance.number_of_states
        return super().form_valid(form)


# TODO: zmienić na defaultowy plik instrukcji przy kazdej zmianie
class MachineUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TuringMachineDB
    fields = ['title', 'is_decisive', 'number_of_states', 'alphabet', 'starting_index', 'empty_sign']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        if form.instance.initial_alphabet != form.instance.alphabet \
                or form.instance.initial_number_of_states != form.instance.number_of_states:
            # form.instance.prepare_excel()
            form.instance.excel_empty = True
            form.instance.initial_number_of_states = form.instance.number_of_states
            form.instance.initial_alphabet = form.instance.alphabet
        return super().form_valid(form)

    def test_func(self):
        machine = self.get_object()
        return self.request.user == machine.author


# TODO: NOT WORKING
class MachineUpdateViewFile(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TuringMachineDB
    fields = ['instructions']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def test_func(self):
        machine = self.get_object()
        return self.request.user == machine.author


class MachineDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TuringMachineDB
    success_url = '/TuringSimulator/'

    def test_func(self):
        machine = self.get_object()
        return self.request.user == machine.author


class ExampleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ExampleDB
    # success_url = '/TuringSimulator/'

    def test_func(self):
        machine = self.get_object()
        return self.request.user == machine.author

    def get_success_url(self, **kwargs):
        return '/TuringSimulator/machine/' + str(self.object.machine_id)

