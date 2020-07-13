"""NEweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from shop.views import SellerView, AddItemView, EditItemView, ProductDeleteView, SellerShop
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('shop/', include('shop.urls')),
    path('seller/<str:name>/page/', SellerView.as_view(), name='seller-page'),
    path("seller/addItem/", AddItemView.as_view(), name="addItem"),
    path("seller/shop/", SellerShop.as_view(), name="sellershop"),    
    path("seller/product/<int:myid>/edit/", EditItemView.as_view(), name="edititem"),
    path('seller/product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('', views.index)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
