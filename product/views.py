from django.shortcuts import get_object_or_404, render
from .models import Product, Our_Brands, Category, Featured_Categories
from . models import *
def home(request):
   

    top_selling = Product.objects.filter(section='top_selling')
    all_natural = Product.objects.filter(section='all_natural')
    exclusive_combo = Product.objects.filter(section='exclusive_combo')
    premium_dates = Product.objects.filter(section='premium_dates')
    cooking_essentials = Product.objects.filter(section='cooking_essentials')
    organic_certified = Product.objects.filter(section='organic_certified')
    just_for_you = Product.objects.filter(section='just_for_you')
    
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
    product = Product.objects.get(product_slug=product_slug)
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