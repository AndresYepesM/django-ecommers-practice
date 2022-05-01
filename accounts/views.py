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
from django.contrib import messages, auth
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from carts.views import _cart_id
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
import requests
# Create your views here.


#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage




# Registration form with abstract users and errors messages
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_num = form.cleaned_data['phone_num']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_num = phone_num    
            user.save()

            # createing a user profile.
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default.png'
            profile.save()

            # USER ACTIVATION:
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/accounts_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Check your email address to activate your account!')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    
    context = {
        'form':form
    }
    return render(request, 'accounts/register.html', context)




def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # este try block solo esta analizando si hay un objeto carro
            # si es verdadero se agregara a la session del ususario
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    # aqui agarra los productos y su variaciones con el ID
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # aqui vamos agarrar el  carro del ususario y los productos con sus variacioes
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'Your are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')




def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! your account is activate!')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')



@login_required(login_url='login')
def dashboard(request):
    orders =Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    order_count = orders.count()
    context = {
        'order_count':order_count
    }
    return render(request, 'accounts/dashboard.html', context)




def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your pasword'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Passoword reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Accounts does not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')




def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')




def resetPassword(request):
    if request.method == 'POST':
        new_password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        have_uper = 0

        if new_password == confirm_password:
            if len(new_password) >=8:
                for i in new_password:
                    if i.isupper():
                        have_uper += 1
                if have_uper >= 1:
                    uid = request.session.get('uid')
                    user = Account.objects.get(pk=uid)
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password reset successful')
                    return redirect('login')
                else:
                    messages.error(request, 'Password need a least 1 uppercase Characters')
                    return redirect('resetPassword')
            else:
                messages.error(request, 'Password need at least 8 Characters, please Try again')
                return redirect('resetPassword')
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/reset_password.html')


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context ={'orders':orders,}
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context ={
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile':userprofile
    }

    return render(request, 'accounts/edit_profile.html', context)



@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']
        user = Account.objects.get(username__exact=request.user.username)
        count = 0

        if new_password == confirm_new_password:
            success = user.check_password(current_password)
            if success:
                if len(new_password) >= 8:
                    for i in new_password:
                        if i.isupper():
                            count += 1
                
                    if count >= 1:
                        user.set_password(new_password)
                        user.save()
                        auth.logout(request)
                        messages.success(request, 'You password has been updated successfully.')
                        return redirect('change_password')
                    else:
                        messages.error(request, 'The new password need at least 1 Uppercase character please try again!')
                        return redirect('change_password')
                else:
                    messages.error(request, 'The new password need at least 8 character please try again!')
                    return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'The new pasword not match.')
            return redirect('change_password')
    else:
        return render(request, 'accounts/change_password.html')



@login_required(login_url='login')
def order_detail(request, order_id):      # el doble "_" significa que agarrar todo los productos de la orden y los datos de la orden en si  
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }

    return render(request, 'accounts/order_detail.html', context)