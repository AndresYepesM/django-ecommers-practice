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
from .models import Product
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
# Create your views here.


# braking slug add this ↓↓↓↓↓↓↓
def store(request, category_slug=None):

    # Display by category
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        items = Product.objects.filter(category=categories, is_available=True)
        product_count = items.count()
    else:
        # Display all the products  
        items= Product.objects.all().filter(is_available=True)
        product_count = items.count()

    context = {
        'items':items,
        'product_count': product_count
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):

    try:
        single_product =Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e

    context = {
        'item': single_product,
        'in_cart': in_cart
    }
    return render(request, 'store/product_detail.html', context)