from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
import datetime
import json
from store.models import Product
from carts.models import CartItem, Cart
from .forms import OrderForm        
from .models import Order, Payments, OrderProduct
from django.core.mail import EmailMessage
from django.template.loader import render_to_string



# Create your views here.
def payments(request):
    body =json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # ya que temeos los datos de paypal mediante js y json los 
    # metemos dentro del model pagos
    payment = Payments(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # luego de almacenar la transaccion de la orden
    # se movera los productos a la tabla de orden 
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        # producto y se restara la cantidad de 
        # stock de dicho producto 
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    #limpiar el carro
    CartItem.objects.filter(user=request.user).delete()

    #  co su respectivo email
    mail_subject = 'Thanks you for order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()


    # y mandar los datos vuelta a Paypal
    data = {
        'order_number':order.order_number,
        'transID': payment.payment_id
    }
    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user

    # Vamos a verificar si el carro tiene articulos o no
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store')

    # aqui calculamos nuevamente el sub_total, total y los taxes
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total  += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # almacenaremos los datos del formulario
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line1 = form.cleaned_data['address_line1']
            data.address_line2 = form.cleaned_data['address_line2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # generaremos un numero de orden para idetificar de forma precisa
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items': cart_items,
                'total': total,
                'tax':tax,
                'grand_total':grand_total
            }
            return render(request, 'orders/payments.html', context)
        else:
            messages.error(request, 'Something went wrong.')
            return redirect('place_order')
    else:
        return redirect('checkout')


def order_compelte(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payments.objects.get(payment_id=transID)

        subtotal = 0
        for i in order_products:
            subtotal += i.product_price * i.quantity

        context={
            'order': order,
            'order_products': order_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }

        return render(request, 'orders/order_complete.html', context)

    except (Payments.DoesNotExist, Order.DoesNotExist):
        return redirect('home')