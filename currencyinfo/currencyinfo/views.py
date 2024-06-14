from django.shortcuts import render
import requests


def dashboard(request):
    return render(request, 'index.html')


