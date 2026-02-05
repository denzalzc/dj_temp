from django.shortcuts import render
from .models import Product
from django.http import Http404
from random import randint


def index(request):
    products = Product.objects.all()

    return render(request, '_home.html', {'products': products})

def catch_all(request, path=''):
    if path == '.htaccess' or path.endswith('/.htaccess'):
        return render(request, 'htaccess.html', status=200)

    additional = '__a great mind requires great discipline__' * randint(10, 5000)

    return render(request, '404.html', {'additional': additional})