
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils.crypto import get_random_string
from .models import * # আপনার সব মডেল একসাথে ইম্পোর্ট করা হলো
from decimal import Decimal
# ==========================================
# ১. হোম এবং প্রোডাক্ট পেজ ভিউজ (Home & Products)
# ==========================================

def home(request):
    # সেকশন অনুযায়ী প্রোডাক্ট ফিল্টার
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
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email')
        first_name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        current_user = request.user

        # ইউজার যদি লগইন করা না থাকে, তবে অটো অ্যাকাউন্ট হ্যান্ডেল করা হবে
        if not current_user.is_authenticated:
            # চেক করা হচ্ছে এই ইমেইলে অলরেডি অ্যাকাউন্ট আছে কিনা
            user_exists = User.objects.filter(email=email).first()
            
            if user_exists:
                # অ্যাকাউন্ট থাকলে তাকেই কারেন্ট ইউজার ধরা হবে এবং লগইন করানো হবে
                current_user = user_exists
                login(request, current_user)
            else:
                # অ্যাকাউন্ট না থাকলে নতুন ইউজার তৈরি করা হবে
                username = email.split('@')[0] + get_random_string(length=4)  # ইউনিক ইউজারনেম তৈরি
                password = get_random_string(length=10)  # ব্যাকগ্রাউন্ডে পাসওয়ার্ড জেনারেট করা
                
                current_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name
                )
                # নতুন ইউজারকে সিস্টেমে অটো লগইন করানো
                login(request, current_user)

            # গেস্ট কার্টটিকে এখন নতুন ইউজারের অ্যাকাউন্টের সাথে লিঙ্ক করে দেওয়া
            cart.user = current_user
            cart.save()

        # >>> এখানে আপনার অর্ডার ক্রিয়েশন লজিক আসবে (Order Model অনুযায়ী) <<<
        # উদাহরণ: order = Order.objects.create(user=current_user, address=address, phone=phone...)
        
        # অর্ডার হয়ে যাওয়ার পর সেশন কার্ট ডিলিট করা
        if 'cart_id' in request.session:
            del request.session['cart_id']
            
        return render(request, 'order_success.html', {'user': current_user})

    grand_total = sum(item.total_price for item in cart_items)
    return render(request, 'product/checkout.html', {'cart_items': cart_items, 'grand_total': grand_total})

def checkout_and_order(request):
    """ ১. শুধুমাত্র চেকআউট পেজ এবং কার্ট সামারি দেখানোর ভিউ """
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('home')

    # এখানে Decimal দিয়ে টাইপ এররটি ফিক্স করা হলো
    cart_subtotal = sum(item.total_price for item in cart_items)
    delivery_charge = Decimal('130.00') # স্ট্রিং আকারে পাস করলে নিখুঁত ডেসিমাল কনভার্ট হয়
    cart_grand_total = cart_subtotal + delivery_charge

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'delivery_charge': delivery_charge,
        'cart_grand_total': cart_grand_total,
    }
    return render(request, 'product/checkout.html', context)


def place_order(request):
    """ ২. 'place-order/' পাথের জন্য ডেডিকেটেড ভিউ যা ফর্ম সাবমিশন হ্যান্ডেল করবে """
    if request.method == "POST":
        cart = get_or_create_cart(request)
        cart_items = cart.items.all()
        
        if not cart_items:
            return redirect('home')

        # ফর্ম থেকে ডাটা রিসিভ করা
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        district = request.POST.get('district')
        upazila = request.POST.get('upazila')
        payment_method = request.POST.get('payment_method')
        special_notes = request.POST.get('special_notes')

        current_user = request.user

        # অটো অ্যাকাউন্ট তৈরি করার লজিক (লগইন না থাকলে)
        if not current_user.is_authenticated:
            username = f"user_{phone}" if phone else get_random_string(length=8)
            email = f"{username}@ghorerbazarclone.com"
            
            user_exists = User.objects.filter(username=username).first()
            
            if user_exists:
                current_user = user_exists
                login(request, current_user)
            else:
                password = get_random_string(length=10)
                current_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=full_name
                )
                login(request, current_user)

            cart.user = current_user
            cart.save()

        # অর্ডারের মোট টাকার হিসাব (এখানেও Decimal ব্যবহার করা হয়েছে)
        cart_subtotal = sum(item.total_price for item in cart_items)
        delivery_charge = Decimal('130.00') 
        cart_grand_total = cart_subtotal + delivery_charge

        # অর্ডার মডেলে মেইন ডেটা সেভ করা
        order = Order.objects.create(
            user=current_user,
            full_name=full_name,
            phone=phone,
            address=f"{address}, {upazila}, {district}",
            payment_method=payment_method,
            special_notes=special_notes,
            subtotal=cart_subtotal,
            delivery_charge=delivery_charge,
            total_amount=cart_grand_total,
            status='Pending'
        )

        # OrderItem মডেলে কার্টের প্রোডাক্টগুলো লুপ করে সেভ করা
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.discount_price if item.product.discount_price else item.product.price,
                quantity=item.quantity
            )

        # কার্ট ক্লিয়ার এবং সেশন আইডি ডিলিট করা
        cart.delete()
        if 'cart_id' in request.session:
            del request.session['cart_id']

        return render(request, 'order_success.html', {'user': current_user, 'order': order})

    return redirect('checkout_and_order')