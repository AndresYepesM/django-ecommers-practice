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
from django.db.models import Q
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.


# braking slug add this ↓↓↓↓↓↓↓
def store(request, category_slug=None):

    # Display by category
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        items = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(items, 3)
        page = request.GET.get('page')
        paged_items = paginator.get_page(page)
        product_count = items.count()
    else:
        # Display all the products  
        items = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(items, 3)
        # page se puede cambiar
        page = request.GET.get('page')
        paged_items = paginator.get_page(page)
        product_count = items.count()

    context = {
        'items':paged_items,
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


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            items = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = items.count()
    context={
        'items':items,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)