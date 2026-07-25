from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
#request handles the request from the user 
# and returns a response
def say_hello(request):
    return HttpResponse('Hello World!')