from django.db import models

# Create your models here.
from django.db import models
from datetime import date

# ----------------------
# User Model
# ----------------------
class User(models.Model):
    usid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dob = models.DateField()
    number = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    nationality = models.CharField(max_length=50)
    address = models.TextField()

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return self.name


# ----------------------
# Seller Model
# ----------------------
class Seller(models.Model):
    sid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dob = models.DateField()
    number = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    nationality = models.CharField(max_length=50)
    address = models.TextField()
    shop_name = models.CharField(max_length=255)
    gst_no = models.CharField(max_length=50)

    # Optional payment reference
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, null=True, blank=True, db_column='pay_id', related_name='seller_payment'
    )

    class Meta:
        managed = False
        db_table = 'seller'

    def __str__(self):
        return self.shop_name


# ----------------------
# Delivery Hub Model
# ----------------------
class DeliveryHub(models.Model):
    hub_id = models.AutoField(primary_key=True)
    hub_name = models.CharField(max_length=255)
    address = models.TextField()
    pin = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    user_no = models.IntegerField()
    product_no = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'delivery_hub'

    def __str__(self):
        return self.hub_name


# ----------------------
# Issue Model
# ----------------------
class Issue(models.Model):
    issue_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='issues')
    issue_type = models.CharField(max_length=100)
    issue_describe = models.TextField()
    issue_status = models.CharField(max_length=50)
    raised_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'issue'

    def __str__(self):
        return f"Issue {self.issue_id} - {self.issue_type}"


# ----------------------
# Payment Model
# ----------------------
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    delivery = models.ForeignKey(DeliveryHub, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField()
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='payments')

    class Meta:
        managed = False
        db_table = 'payment'

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"


# ----------------------
# Review Model
# ----------------------
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    review_text = models.TextField()
    review_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'review'

    def __str__(self):
        return f"Review {self.review_id} - {self.rating} stars"


# ----------------------
# Product Model
# ----------------------
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    real_price = models.FloatField()
    discount_price = models.FloatField()
    stock_quantity = models.IntegerField()
    product_type = models.CharField(max_length=100)
    product_status = models.CharField(max_length=50)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products')

    class Meta:
        managed = False
        db_table = 'product'

    def __str__(self):
        return f"{self.name} - {self.brand}"


# ----------------------
# Platform Model
# ----------------------
class Platform(models.Model):
    platform_id = models.AutoField(primary_key=True)
    platform_name = models.CharField(max_length=255)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='platforms')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='platforms')

    class Meta:
        managed = False
        db_table = 'platforms'

    def __str__(self):
        return self.platform_name
