from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
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
        if self.discount_price and self.price > self.discount_price:
            return self.price - self.discount_price
        return 0
    
    def get_save_percent(self):
        if self.discount_price and self.price > 0:
            saving = self.price - self.discount_price
            return (saving / self.price) * 100
        return 0

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
    




class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} - User: {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.discount_price
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    PAYMENT_CHOICES = (
        ('cod', 'Cash On Delivery'),
        ('online', 'Online Payment'),
        ('bkash', 'Bkash'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    special_notes = models.TextField(null=True, blank=True)
    
    # প্রাইসিং ট্র্যাকিং
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=130.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"


class OrderItem(models.Model):
    # একটি অর্ডারের অধীনে অনেকগুলো আইটেম থাকতে পারে (ForeignKey)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # আপনার Product মডেল
    price = models.DecimalField(max_digits=10, decimal_places=2) # অর্ডারের সময়কার দাম
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"

    @property
    def total_price(self):
        return self.price * self.quantity


