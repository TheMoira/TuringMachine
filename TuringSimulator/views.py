from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import TuringMachineDB, ExampleDB
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadFileForm
from django.templatetags.static import static

# main page
def index(request):
    # return HttpResponse("<h1>Turing Machine Simulator</h1>")
    return render(request, 'TuringSimulator/index.html')


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
    # f = example.example_steps_file
    # f.open(mode='r')
    # lines = f.read()
    # print(lines)
    # f.close()
    # path = example.example_steps_file.path
    lines = example.example_steps
    scratched = static('TuringSimulator/resources/Scratched.png')
    metal = static('TuringSimulator/resources/metal_texture.jpg')
    context = {
        'lines': lines,
        'scratched': scratched,
        'metal':metal,
        'machine_id':machine_id,
    }
    return render(request, 'TuringSimulator/simulation.html', context)
    # return render(request, 'TuringSimulator/simulation/simulation.html')


def download_instruction(request, object_id):
    machine = get_object_or_404(TuringMachineDB, pk=object_id)
    file = machine.instructions
    path = machine.instructions.path
    response = HttpResponse(file.read(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=' + path
    return response


def upload_instruction(request, object_id):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            machine = get_object_or_404(TuringMachineDB, pk=object_id)
            print(machine.instructions.name)
            machine.instructions = file
            print('2 ' + machine.instructions.name)
            machine.excel_empty = False
            machine.save()
            # return HttpResponseRedirect('TuringSimulator/machine/' + str(object_id))
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
    # TODO: validate czy zgodne z alfabetem + żeby dla konkretnej maszyny
    model = ExampleDB
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.machine = self.t_machine
        # form.instance.prepare_instruction_steps_file()
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
            form.instance.prepare_excel()
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

