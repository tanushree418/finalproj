from django.db import models
from django.contrib.auth.models import User

# Create your models here.

CATEGORY_CHOICES = (
    ('Textile', 'Textile'),
    ('Handicraft', 'Handicraft')
)

SUBCATEGORY_CHOICES = (
    ('ASS', 'Assam'),
    ('MAN', 'Manipur'),
    ('ARU', 'Arunachal Pradesh'),
    ('TRI', 'Tripura'),
    ('SIK', 'Sikkim'),
    ('NAG', 'Nagaland'),
    ('MEG', 'Meghalaya'),
    ('MIZ', 'Mizoram'),
)


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="Textile", choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=50, default="ASS", choices=SUBCATEGORY_CHOICES)
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    quantity = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    pub_date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='shop/images', default="")

    def __str__(self):
        return f"{self.product_name} - INR{self.price} - {self.quantity}"
    
    def get_quantity_available(self):
        return int(self.quantity - self.quantity_sold)


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")


    def __str__(self):
        return self.name

class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.AutoField(primary_key=True)
    ref_code = models.CharField(max_length=20)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField( default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111, default="")

class OrderUpdate(models.Model):
    update_id  = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."