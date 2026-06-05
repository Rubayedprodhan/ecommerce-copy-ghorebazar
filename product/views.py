
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils.crypto import get_random_string
from .models import * 
from decimal import Decimal
from sslcommerz_lib import SSLCOMMERZ 
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
def home(request):
    top_selling = Product.objects.filter(section='top_selling')
    all_natural = Product.objects.filter(section='all_natural')
    exclusive_combo = Product.objects.filter(section='exclusive_combo')
    premium_dates = Product.objects.filter(section='premium_dates')
    cooking_essentials = Product.objects.filter(section='cooking_essentials')
    organic_certified = Product.objects.filter(section='organic_certified')
    just_for_you = Product.objects.filter(section='just_for_you')
    
    # ব্র্যান্ড এবং ক্যাটাগরি ডেটা fetch
    brand = Our_Brands.objects.all()
    category = Category.objects.all()  
    featured_Categories = Featured_Categories.objects.all()

    context = {
        'top_selling': top_selling,
        'all_natural': all_natural,
        'exclusive_combo': exclusive_combo,
        'premium_dates': premium_dates,
        'cooking_essentials': cooking_essentials,
        'organic_certified': organic_certified,
        'just_for_you': just_for_you,
        'brand': brand,
        'Category': category,  
        'Featured_Categories': featured_Categories,
    }
    return render(request, 'home/home.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, product_slug=product_slug)
    return render(request, 'product/product_detail.html', {'product': product})


def category_product(request, category_name):
    category = get_object_or_404(Featured_Categories, name=category_name)
    products = Product.objects.filter(Featured_Categories=category)
    
    return render(request, 'product/category_products.html', {
        'category': category,
        'products': products
    })


def brand_products(request, brand_name):
    brand = get_object_or_404(Our_Brands, name=brand_name)
    products = Product.objects.filter(brands=brand)
    
    return render(request, 'product/brand_products.html', {
        'brand': brand,
        'products': products
    })


# ==========================================
# ২. সেশন ভিত্তিক কার্ট মেকানিজম (লগইন ছাড়া কার্ট)
# ==========================================

def get_or_create_cart(request):
    """ লগইন বা আন-লগইন দুই অবস্থাতেই সঠিক কার্ট অবজেক্ট রিটার্ন করবে """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        # গেস্ট ইউজারের জন্য সেশনে কার্ট আইডি সেভ রাখা
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user=None)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(user=None)
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id
        return cart


def add_to_cart(request, product_id):
    """ AJAX এর মাধ্যমে কার্টে প্রোডাক্ট যুক্ত করার ভিউ """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item.save()
            
        return JsonResponse({'status': 'success', 'message': 'Product added successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def update_cart_quantity(request, item_id):
    """ ড্রয়ারের প্লাস, মাইনাস এবং ডিলিট বাটন হ্যান্ডেল করার ভিউ """
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get('action')
        
        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()  # ১ এর কম হলে আইটেম রিমুভ হবে
        elif action == 'delete':
            item.delete()
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def fetch_drawer_cart(request):
    """ ড্রয়ার ওপেন বা আপডেট হলে নতুন HTML টুকরোটি জেনারেট করে রিটার্ন করার ভিউ """
    cart = get_or_create_cart(request)
    cart_items = cart.items.all().order_by('id')
    grand_total = sum(item.total_price for item in cart_items)
    
    return render(request, 'partials/drawer_cart_content.html', {
        'cart_items': cart_items,
        'grand_total': grand_total
    })


def cart_detail(request):
    """ মেইন সম্পূর্ণ কার্ট পেজ দেখার ভিউ """
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    grand_total = sum(item.total_price for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'cart_detail.html', context)


# ==========================================
# ৩. অটো অ্যাকাউন্ট ক্রিয়েশন এবং অর্ডার ভিউ
# ==========================================




def checkout_and_order(request):
    # ১. কার্ট এবং কার্ট আইটেম গেট করা
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('home')

    # ২. যখন ইউজার ফর্ম সাবমিট করবে (POST Request)
    if request.method == "POST":
        email = request.POST.get('email')
        first_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method') # 'cod' অথবা 'sslcommerz' আসবে

        current_user = request.user

        # গেস্ট ইউজার হ্যান্ডেলিং (লগইন না থাকলে অটো অ্যাকাউন্ট তৈরি)
        if not current_user.is_authenticated:
            user_exists = User.objects.filter(email=email).first()
            if user_exists:
                current_user = user_exists
                login(request, current_user)
            else:
                username = email.split('@')[0] + get_random_string(length=4)
                password = get_random_string(length=10)
                current_user = User.objects.create_user(
                    username=username, email=email, password=password, first_name=first_name
                )
                login(request, current_user)

            cart.user = current_user
            cart.save()

        # টোটাল অ্যামাউন্ট হিসাব
        cart_subtotal = sum(item.total_price for item in cart_items)
        delivery_charge = Decimal('130.00')
        cart_grand_total = cart_subtotal + delivery_charge
        
        # ইউনিক ট্রানজেকশন আইডি তৈরি (ডাটাবেজে সেভ এবং SSL-এ পাঠানোর জন্য)
        tran_id = get_random_string(length=12).upper() 

        # >>> এখানে আপনার মডেল অনুযায়ী Order এবং OrderItem অবজেক্ট তৈরি করুন <<<
        # উদাহরণ:
        # order = Order.objects.create(user=current_user, total_amount=cart_grand_total, transaction_id=tran_id, payment_method=payment_method, status='Pending')
        # for item in cart_items:
        #     OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)

        # ----------------------------------------------------
        # অপশন A: ইউজার যদি SSLCommerz (Online) সিলেক্ট করে
        # ----------------------------------------------------
        if payment_method == 'sslcommerz':
            # আপনার প্রোভাইড করা SSLCommerz স্যান্ডবক্স ডেমো ক্রেডেনশিয়াল
            settings = {
                'store_id': 'copyg6a2315e5c785d',       
                'store_pass': 'copyg6a2315e5c785d@ssl', 
                'issandbox': True            # লাইভ করার সময় False করবেন
            }
            # অফিসিয়াল লাইব্রেরির স্ট্যান্ডার্ড ক্লাস নেম SSLCommerz ব্যবহার করা হয়েছে
            sslcz = SSLCommerz(settings)
            
            post_body = {
                'total_amount': float(cart_grand_total),
                'currency': 'BDT',
                'tran_id': tran_id,
                'success_url': request.build_absolute_uri(reverse('payment_success')),
                'fail_url': request.build_absolute_uri(reverse('payment_fail')),
                'cancel_url': request.build_absolute_uri(reverse('payment_cancel')),
                'emi_option': 0,
                'cus_name': first_name if first_name else current_user.username,
                'cus_email': email,
                'cus_phone': phone if phone else '01700000000',
                'cus_add1': address if address else 'Dhaka',
                'cus_city': 'Dhaka',
                'cus_country': 'Bangladesh',
                'shipping_method': 'NO',
                'num_of_item': cart_items.count(),
                'product_name': 'Cart Items',
                'product_category': 'Ecommerce',
                'product_profile': 'general',
            }

            response = sslcz.createSession(post_body)
            
            if 'GatewayPageURL' in response:
                # পেমেন্ট পেজে রিডাইরেক্ট করা হচ্ছে (অনলাইন পেমেন্ট সফল হলে 'payment_success' ভিউতে কার্ট ডিলিট হবে)
                return redirect(response['GatewayPageURL'])
            else:
                return render(request, 'payment_error.html', {'error': response})

        # ----------------------------------------------------
        # অপশন B: ইউজার যদি Cash on Delivery (COD) সিলেক্ট করে
        # ----------------------------------------------------
        else:
            # ক্যাশ অন ডেলিভারিতে সরাসরি কার্ট ডিলিট/খালি করা হবে
            cart_items.delete() 
            
            if 'cart_id' in request.session:
                del request.session['cart_id']
                
            return render(request, 'order_success.html', {'user': current_user})

    # ৩. যখন ইউজার প্রথমবার চেকআউট পেজে আসবে (GET Request)
    cart_subtotal = sum(item.total_price for item in cart_items)
    delivery_charge = Decimal('130.00')
    cart_grand_total = cart_subtotal + delivery_charge

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'delivery_charge': delivery_charge,
        'cart_grand_total': cart_grand_total,
    }
    return render(request, 'product/checkout.html', context)


# ----------------------------------------------------
# SSLCommerz পেমেন্ট রেসপন্স হ্যান্ডেলার ভিউজ
# ----------------------------------------------------

@csrf_exempt
def payment_success(request):
    """ অনলাইন পেমেন্ট সফল হলে এই ভিউ কাজ করবে """
    if request.method == 'POST':
        payment_data = request.POST
        tran_id = payment_data.get('tran_id')
        
        # ১. এখানে ডাটাবেজে অর্ডারের স্ট্যাটাস 'Paid' আপডেট করতে পারেন
        # order = Order.objects.get(transaction_id=tran_id)
        # order.status = 'Paid'
        # order.save()
        
        # ২. পেমেন্ট নিশ্চিত হওয়ার পর অনলাইন ইউজারের কার্ট খালি করা
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        
        if 'cart_id' in request.session:
            del request.session['cart_id']
        
        return render(request, 'payment_success.html', {'tran_id': tran_id})
    return redirect('home')

@csrf_exempt
def payment_fail(request):
    """ অনলাইন পেমেন্ট ফেইল হলে এই ভিউ কাজ করবে """
    if request.method == 'POST':
        payment_data = request.POST
        tran_id = payment_data.get('tran_id')
        # এখানে অর্ডারের স্ট্যাটাস 'Failed' আপডেট করতে পারেন
        return render(request, 'payment_fail.html', {'tran_id': tran_id})
    return redirect('home')

@csrf_exempt
def payment_cancel(request):
    """ ইউজার পেমেন্ট ক্যানসেল করলে এই ভিউ কাজ করবে """
    return render(request, 'payment_cancel.html')
# def checkout_and_order(request):
#     cart_items = []  
#     cart_subtotal = 650.00
#     delivery_charge = 130.00
#     cart_grand_total = cart_subtotal + delivery_charge
    
#     context = {
#         'cart_items': cart_items,
#         'cart_subtotal': cart_subtotal,
#         'delivery_charge': delivery_charge,
#         'cart_grand_total': cart_grand_total,
#     }
#     return render(request, 'product/checkout.html', context)





def place_order(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        district = request.POST.get('district')
        upazila = request.POST.get('upazila')
        special_notes = request.POST.get('special_notes')
        
       
        return redirect('order_success')
        
    return redirect('checkout_and_order')


def sslcommerz_initiate(request):
    """২. SSLCommerz পেমেন্ট গেটওয়ে ইনিশিয়েট করার ভিউ"""
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        grand_total = request.POST.get('grand_total') # বা সেশন/কার্ট থেকে টোটাল ক্যালকুলেট করুন
        
        """
        settings = { 'store_id': 'your_store_id', 'store_pass': 'your_pass', 'issandbox': True }
        sslcommez = SSLCommerz(settings)
        post_body = {}
        post_body['total_amount'] = grand_total
        post_body['currency'] = "BDT"
        post_body['tran_id'] = "TRAN_12345" # ইউনিক ট্রানজেকশন আইডি
        post_body['success_url'] = "http://127.0.0.1:8000/payment/sslcommerz/success/"
        post_body['fail_url'] = "http://127.0.0.1:8000/payment/sslcommerz/fail/"
        
        response = sslcommez.createSession(post_body)
        return redirect(response['GatewayPageURL']) # সরাসরি SSLCommerz পেমেন্ট পেজে রিডাইরেক্ট করবে
        """
        
        return redirect('order_success')
    return redirect('checkout_and_order')


def bkash_initiate(request):
    if request.method == "POST":
       
        request.session['bkash_customer_name'] = request.POST.get('full_name')
        request.session['bkash_phone'] = request.POST.get('phone')
        request.session['bkash_address'] = f"{request.POST.get('address')}, {request.POST.get('upazila')}, {request.POST.get('district')}"
        
        return redirect('bkash_payment_page')
    return redirect('checkout_and_order')


def bkash_payment_page(request):
    context = {
        'customer_name': request.session.get('bkash_customer_name'),
        'phone': request.session.get('bkash_phone'),
        'address': request.session.get('bkash_address'),
    }
    return render(request, 'product/bkash_payment.html', context)


def order_success(request):
    return render(request, 'product/order_success.html')