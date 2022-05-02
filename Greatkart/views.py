from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from datetime import date
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from store.models import Product, ReviewRating

def home(request):
    items= Product.objects.all().filter(is_available=True).order_by('created_date')

    # calculando el rate 
    for item in items:
        reviews = ReviewRating.objects.filter(product_id=item.id, status=True)

    context = {
        'items':items,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)


def contact_me(request):
    return render(request, 'contact/email.html')

def call_me(request):
    return render(request, 'contact/callme.html')