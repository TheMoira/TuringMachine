from django.shortcuts import render
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