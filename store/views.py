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
from .models import Product, ReviewRating, ProductGallery
from .forms import ReviewForm
from category.models import Category
from django.db.models import Q
from carts.views import _cart_id
from carts.models import CartItem
from orders.models import OrderProduct
from django.contrib import messages
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

    if request.user.is_authenticated:
        # aqui estamos ferificando si el ususario ha comprando un articulo
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None
        
    # calculando el rate 
    reviews = ReviewRating.objects.filter(product_id=single_product, status=True)

    #Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'item': single_product,
        'in_cart': in_cart,
        'order_product': order_product,
        'reviews': reviews,
        'product_gallery': product_gallery,
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


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! your review has been updated')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you!, you review has been sufmitted')
                return redirect(url)