from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import TuringMachineDB, ExampleDB
from django.http import HttpResponse


# main page
def index(request):
    # return HttpResponse("<h1>Turing Machine Simulator</h1>")
    return render(request, 'TuringSimulator/index.html')


# about page
def about(request):
    return render(request, 'TuringSimulator/about.html')


def stylesheet(request):
    return render(request, '../static/TuringSimulator/main.css')


def simulation(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = 'public'
    # TODO: zrobic tu transformacje z turing_utils zeby szlo do symulacji
    queryset = ''
    context = {
        'data': queryset,
        'user': user,
    }
    return render(request, 'TuringSimulator/simulation/simulation.html', context)
    # return render(request, 'TuringSimulator/simulation/simulation.html')


def download_instruction(request, object_id):
    machine = get_object_or_404(TuringMachineDB, pk=object_id)
    file = machine.instructions
    path = machine.instructions.path
    response = HttpResponse(file.read(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=' + path
    return response


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
        return super().form_valid(form)


# TODO: zmienić na defaultowy plik instrukcji przy kazdej zmianie
class MachineUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TuringMachineDB
    fields = ['title', 'is_decisive', 'number_of_states', 'alphabet', 'starting_index', 'empty_sign']

    def form_valid(self, form):
        form.instance.author = self.request.user
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
        form.instance.excel_filled = True
        return super().form_valid(form)

    def test_func(self):
        machine = self.get_object()
        return self.request.user == machine.author


# TODO: clean file django_cleanup not working
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
