from .models import Product
from django import forms
from django.forms import ModelForm


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name','category', 'subcategory', 
                    'price', 'desc', 'quantity', 'image')


class ProductEditForm(forms.ModelForm):
    image = forms.FileField(required = False)
    class Meta:
        model = Product
        fields = ('product_name','category', 'subcategory', 
                    'price', 'desc', 'quantity', 'image')
