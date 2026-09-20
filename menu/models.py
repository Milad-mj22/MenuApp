from django.db import models

# Create your models here.





class mother_food(models.Model):


    name = models.CharField(max_length=200)
    # describe = models.CharField(max_length=800)
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-name']




class FoodRawMaterial(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    mother = models.ForeignKey(mother_food, on_delete= models.CASCADE,related_name='mother_food_id',blank=True,null=True)
    name = models.CharField(max_length=200,null=True,blank=True)
    # JSON data
    data = models.JSONField(blank=True,null=True)
    price = models.IntegerField(default=0,blank=True,null=True)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)  # Added field for image
    details = models.CharField(max_length=2000,default='',blank=True,null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)  # Discount percentage
    priority = models.IntegerField(default=0)  # New field for priority
    is_new = models.BooleanField(default=False)  # مشخص می‌کند که محصول در این شعبه تمام شده است یا نه


    def __str__(self):
        return str(self.price)

    def discounted_price(self):
        """
        Calculates the price after applying the discount.
        If discount is set to 0, returns the original price.
        """
        if self.discount > 0:
            discount_amount = (self.discount / 100) * self.price
            return self.price - discount_amount
        return self.price

    class Meta:
        ordering = ['-price']





class RestaurantBranch(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)  # ظرفیت انبار



    def __str__(self):
        return self.name



class SoldOutStatus(models.Model):
    branch = models.ForeignKey(RestaurantBranch, on_delete=models.CASCADE, related_name="sold_out_status")
    product = models.ForeignKey(FoodRawMaterial, on_delete=models.CASCADE, related_name="sold_out_product")
    is_sold_out = models.BooleanField(default=False)  # مشخص می‌کند که محصول در این شعبه تمام شده است یا نه
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.branch.name} - {self.product.name} - {'Sold Out' if self.is_sold_out else 'Available'}"



