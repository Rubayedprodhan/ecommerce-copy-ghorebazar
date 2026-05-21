from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),    
    path('category/<str:category_name>/', views.category_product, name='category_product'),
    path('brand/<str:brand_name>/', views.brand_products, name='brand_products'),
]