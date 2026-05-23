from django.urls import path
from . import views

urlpatterns = [
    # ১. হোম এবং প্রোডাক্ট পেজ ইউআরএল
    path('', views.home, name='home'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),    
    path('category/<str:category_name>/', views.category_product, name='category_product'),
    path('brand/<str:brand_name>/', views.brand_products, name='brand_products'),
    
    # ২. রেগুলার কার্ট এবং চেকআউট পেজ ইউআরএল
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout_and_order, name='checkout_and_order'),
    
    # ৩. লাইভ ড্রয়ার কার্ট মেকানিজম (AJAX/Fetch API ইউআরএল সমূহ)
    # কার্টে প্রোডাক্ট যুক্ত করার জন্য (এটি আপনার জাভাস্ক্রিপ্ট addToCartAjax ফাংশন কল করবে)
    path('cart/add-ajax/<int:product_id>/', views.add_to_cart, name='add_to_cart_ajax'),
    
    # ড্রয়ারের ভেতর প্লাস (+), মাইনাস (-) এবং ডিলিট (✕) বাটন কাজ করানোর জন্য
    path('cart/update-ajax/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    # পেজ রিফ্রেশ ছাড়া ড্রয়ারের ভেতরের HTML লাইভ আপডেট করার জন্য
    path('cart/fetch-drawer/', views.fetch_drawer_cart, name='fetch_drawer_cart'),

    path('checkout/', views.checkout_and_order, name='checkout_and_order'),
    path('place-order/', views.place_order, name='place_order'),
    path('cart/fetch-drawer/', views.fetch_drawer_cart, name='fetch_drawer_cart'),


    path('checkout/place-order/', views.place_order, name='place_order'),
    
    # ২. SSLCommerz পেমেন্ট গেটওয়ে ইনিশিয়েট রুট
    path('payment/sslcommerz/initiate/', views.sslcommerz_initiate, name='sslcommerz_initiate'),
    
    # ৩. bKash পেমেন্ট গেটওয়ে ইনিশিয়েট ও কাস্টম পেজ রুট
    path('payment/bkash/initiate/', views.bkash_initiate, name='bkash_initiate'),
    path('payment/bkash/page/', views.bkash_payment_page, name='bkash_payment_page'),
    
    # ফাইনাল অর্ডার সাকসেস বা থ্যাঙ্ক ইউ পেজ
    path('order/success/', views.order_success, name='order_success'),
]
