# product/context_processors.py

from .models import  Featured_Categories, Cart  # আপনার ক্যাটাগরি মডেলের নাম অনুসারে পরিবর্তন করুন
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
def category_menu(request):
    # ডেটাবেজ থেকে সব ক্যাটাগরি নিয়ে আসা হচ্ছে
    categories = Featured_Categories.objects.all()
    return {
        'menu_categories': categories
    }

def get_cart_data_ajax(request):
    # মনে করি এটি আপনার সেশন বা মডেল ভিত্তিক কার্ট অবজেক্ট
    # cart = Cart(request) 
    
    cart_items = []
    total_amount = 0
    
    # আপনার কার্টের আইটেমগুলোর উপর লুপ চালান (আপনার কার্ট লজিক অনুযায়ী পরিবর্তন করে নেবেন)
    for item in Cart: 
        price = item['product'].discount_price if item['product'].discount_price else item['product'].price
        total_price = float(price) * int(item['quantity'])
        total_amount += total_price
        
        cart_items.append({
            'product_name': item['product'].name,
            'price': str(price),
            'quantity': item['quantity'],
        })

    return JsonResponse({
        'cart_count': len(cart_items), # মোট কয়টি ইউনিক প্রোডাক্ট
        'cart_total': total_amount,    # মোট টাকার পরিমাণ
        'cart_items': cart_items       # প্রোডাক্ট লিস্ট
    })