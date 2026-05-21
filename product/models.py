from django.db import models
from django.utils.text import slugify
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Media/images/category', null=True, blank=True)


    def __str__(self):
        return self.name

class Product_Flag(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Media/images/product_flag')

    def __str__(self):
        return self.name

class Our_Brands(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Media/images/brand')
    Description = models.TextField()

    def __str__(self):
        return self.name

class Featured_Categories(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Media/images/featured')

    def __str__(self):
        return self.name


class Product(models.Model):
  
    SECTION_CHOICES = [
        ('top_selling', 'Top Selling Products'),
        ('all_natural', 'All Natural'),
        ('exclusive_combo', 'Exclusive Combo Deals'),
        ('premium_dates', 'Premium Dates'),
        ('cooking_essentials', 'Cooking Essentials'),
        ('organic_certified', 'Organic Certified'),
        ('just_for_you', 'Just For You'),
    ]
    
    section = models.CharField(max_length=30, choices=SECTION_CHOICES, default='just_for_you')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Media/images/product')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    Quantity = models.IntegerField()
    Description = models.TextField() 
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
   
    brands = models.ForeignKey(Our_Brands, on_delete=models.CASCADE, null=True, blank=True)
    catagory = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    flag = models.ForeignKey(Product_Flag, on_delete=models.CASCADE, null=True, blank=True)
    Featured_Categories = models.ForeignKey(Featured_Categories, on_delete=models.CASCADE, null=True, blank=True)
  
    product_slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    def get_save_amount(self):
        if self.old_price:
            return self.old_price - self.price
        return 0
    
    def get_save_percent(self):
        if self.old_price and self.old_price > 0:
            return ((self.old_price - self.price) / self.old_price) * 100
        return 0
  #  product_id = models.AutoField(primary_key=True)

   

   

    def save(self, *args, **kwargs):
        if not self.product_slug:
            self.product_slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.get_section_display()})"


class Product_Review(models.Model):
    name = models.CharField(max_length=100)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return f"Review by {self.name} on {self.product.name}"
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='Media/images/product_gallery')

    def __str__(self):
        return f"{self.product.name} Gallery Image"
    




class add_to_cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"