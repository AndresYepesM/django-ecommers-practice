from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    
    path('securelogin/', admin.site.urls),

    path('', views.home, name='home'),

    path('store/', include('store.urls')),

    path('cart/', include('carts.urls')),

    path('accounts/', include('accounts.urls')),

    path('orders/', include('orders.urls')),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
