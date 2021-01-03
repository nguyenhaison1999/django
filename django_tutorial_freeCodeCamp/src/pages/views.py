from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def home_view(request, *args, **kwargs):
    # return HttpResponse("<h1>Hello World</h1>")
    context = {"test": "Hello you there!", "list": [123, 321, 213, 312]}
    return render(request, "home.html", context)
