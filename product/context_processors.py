# product/context_processors.py

from .models import  Featured_Categories  # আপনার ক্যাটাগরি মডেলের নাম অনুসারে পরিবর্তন করুন

def category_menu(request):
    # ডেটাবেজ থেকে সব ক্যাটাগরি নিয়ে আসা হচ্ছে
    categories = Featured_Categories.objects.all()
    return {
        'menu_categories': categories
    }