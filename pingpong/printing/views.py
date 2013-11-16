# Create your views here.
from django.shortcuts import render
from pingpong.models import Category


def print_report(request):
    categories = Category.objects.filter(type=Category.SINGLE)
    return render(request, 'print_report.html', dict(categories=categories))
