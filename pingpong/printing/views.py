# Create your views here.
from django.shortcuts import render
from pingpong.bracket.models import Bracket
from pingpong.models import Category


def print_report(request):
    categories = Category.objects.filter(type=Category.SINGLE)
    return render(request, 'print_report.html', dict(categories=categories))


def print_results(request):
    brackets = Bracket.objects.order_by('category', 'id')
    categories_without_groups = Category.objects.filter(bracket__isnull=True, group__isnull=False).distinct()
    return render(request, 'print_results.html', dict(brackets=brackets,
                                                      categories_without_groups=categories_without_groups))
