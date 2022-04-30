from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views



urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),

    path('payments/', views.payments, name='payments'),

    path('order_completed/', views.order_compelte, name='order_complete')
]