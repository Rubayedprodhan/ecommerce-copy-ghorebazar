from django.db import models

# Create your models here.
class Our_Brands(models.Model): # Our_  Brands
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name

class Featured_Categories(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')


class Top_Selling_Products(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField(max_digits=10, decimal_places=2)
    Brand = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    Description = models.CharField(max_length=100)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    brands =
     # অফার দাম (৳২,২০০)

    def __str__(self):
        return self.name

class All_Natural(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField(max_digits=10, decimal_places=2)
    Brand = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    Description = models.CharField(max_length=100)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Exclusive_Combo_Deals(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField(max_digits=10, decimal_places=2)
    Brand = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    Description = models.CharField(max_length=100)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Premium_Dates(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField(max_digits=10, decimal_places=2)
    Brand = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    Description = models.CharField(max_length=100)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Cooking_Essentials(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField(max_digits=10, decimal_places=2)
    Brand = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    Description = models.CharField(max_length=100)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Organic_Certified(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField(max_digits=10, decimal_places=2)
    Brand = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    Description = models.CharField(max_length=100)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Just_For_You(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField(max_digits=10, decimal_places=2)
    Brand = models.CharField(max_length=100)
    Quantity = models.IntegerField()
    Description = models.CharField(max_length=100)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    






