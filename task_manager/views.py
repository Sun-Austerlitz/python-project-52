from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    a = None
    a.hello()  # Creating an error with an invalid line of code
    return HttpResponse("Hello, world. You're at the pollapp index.")


def home(request):
    return render(request, "home.html")
