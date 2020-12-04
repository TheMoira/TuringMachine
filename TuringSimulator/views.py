from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import TuringMachineDB

# main page
def index(request):
    # return HttpResponse("<h1>Turing Machine Simulator</h1>")
    return render(request, 'TuringSimulator/index.html')

# about page
def about(request):
    return render(request, 'TuringSimulator/about.html')

def stylesheet(request):
    return render(request, '../static/TuringSimulator/main.css')


class MachineListView(ListView):
    model = TuringMachineDB
    template_name = 'TuringSimulator/machines.html'
    context_object_name = 'machines'
    ordering = ['name']

class MachineDetailView(DetailView):
    model = TuringMachineDB

