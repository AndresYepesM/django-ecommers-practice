from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from store import views


urlpatterns = [
    path('', views.store, name='store'),

    path('category/<slug:category_slug>/', views.store, name='productos_by_category'),

    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='productos_detail'),

    path('search/', views.search, name='search'),

    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]