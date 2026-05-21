from django.contrib import admin
from .models import *

# Register your models here.
#admin.site.register(Product)
admin.site.register(Product_Review)
admin.site.register(Our_Brands)
admin.site.register(Category)
admin.site.register(Product_Flag)
admin.site.register(Featured_Categories)



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

    prepopulated_fields = {'product_slug': ('name',)}