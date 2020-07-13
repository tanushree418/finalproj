from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from .forms import ProductCreateForm, ProductEditForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from PayTm import Checksum
from django.views.generic import ListView, DetailView, View, RedirectView, DeleteView
# Create your views here.
from django.http import HttpResponse
MERCHANT_KEY = 'Your-Merchant-Key-Here'

import random
import string

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def index(request):
    seller_group = Group.objects.get(name="SELLER")
    if seller_group in request.user.groups.all():
        return redirect('seller-page', request.user.username)
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def seller_items(request, name):
    allProds = []
    is_user = False
    user = User.objects.filter(username__exact=name)[0]
    prods = Product.objects.filter(user__username=name)
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(user__username=name)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    if request.user == user:
        is_user = True

    params = {'allProds':allProds,
                'prods': prods,
                'is_user': is_user,
            }
    return render(request, 'shop/seller.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email, user=request.user)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):

    # Fetch the product using the id
    is_user = False
    product = get_object_or_404(Product, id=myid)
    if request.user == product.user:
        is_user = True
    return render(request, 'shop/prodView.html', {'product':product, 'is_user':is_user})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount, user=request.user)
        order.ref_code = create_ref_code()
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        """
        # return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {

                'MID': 'Your-Merchant-Id-Here',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})
        """
        loads = json.loads(items_json)
        print(loads)
        for i in list(loads.values()):
            prod = Product.objects.get(product_name =str(i[1]))
            prod.quantity_sold += int(i[0])
            prod.save() 
            print("name: ",i[1], "qty: ", i[0])
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        # return redirect('ShopHome')

    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})

def handleSignup(request):
    if request.method == 'POST':
        #Get the post parameters
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        #Check for error inputs
        if len(username) > 10:
            messages.error(request, "Your username must be under 10 characters")
            return redirect('ShopHome')
        if not username.isalnum():
            messages.error(request, "Username should only contain numbers & characters")
            return redirect('ShopHome')
        if pass1 != pass2:
            messages.error(request, "Your passwords did not match")
            return redirect('ShopHome')

        #Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Your account has been successfully created")
        return redirect('ShopHome')

    else:
        return HttpResponse('404 - Not Found')

def handleLogin(request):
    if request.method == 'POST':
         # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username=loginusername,
        password = loginpassword)

    if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect('ShopHome')
    else:
        messages.error(request, "Invalid Credentials, Plaese try again")
        return redirect('ShopHome')

    return HttpResponse('404 - Not Found')

def handleLogout(request):
        logout(request)
        messages.success(request, "Successfully Logged Out")
        return redirect('ShopHome')

class AddItemView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def get(self, request):
        form = ProductCreateForm()
        context = {
            'form': form,
            'page': 'A',
        }
        return render(request, 'shop/product.html', context)

    def post(self, request):
        if request.method == 'POST':
            form = ProductCreateForm(request.POST, request.FILES or None)
            
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()

                return redirect('ShopHome')
        else:
            form = ProductCreateForm()
            
        context = {
            'form': form, 
        }
        return render(request, 'shop/product.html', context)
    
    def test_func(self):
        is_user = False
        user = User.objects.get(username__exact=self.request.user.username)
        seller_g = Group.objects.get(name='SELLER')
        if seller_g in self.request.user.groups.all() or self.request.user.is_superuser:
            is_user = True
        return is_user

class EditItemView(UserPassesTestMixin, LoginRequiredMixin, View):
    model = Product

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['myid']
        item = get_object_or_404(Product, id=slug)
        form = ProductEditForm(instance=item)
        context = {
            'form': form,
            'item': item,
            'page': 'E'
        }
        return render(request, 'shop/product.html', context)
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':            
            slug = self.kwargs['myid']
            item = get_object_or_404(Product, id=slug)
            form = ProductEditForm(request.POST, request.FILES or None, instance=item)
            print((form.errors))

            if form.is_valid():
                post = form.save()
                post.save()
                return redirect('ShopHome')
            else:
                print('An error occured')
                messages.warning(request, f'An error occured')
                return redirect('ShopHome')
        else:
            form = ProductCreateForm()
        context = {
            'form': form, 
        }
        return render(request, 'shop/product.html', context)            
            # return HttpResponseRedirect('shop/index.html',{'product':item})
    
    def test_func(self):
        is_allowed = False
        pk = self.kwargs['myid']
        post = get_object_or_404(Product, pk=pk)
        if self.request.user == post.user: 
            is_allowed = True
        return is_allowed

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Product

    def get(self, request, *args, **kwargs):
        id_ = kwargs['pk']
        prod = get_object_or_404(Product, pk=id_)
        prod.delete()
        print(self.request.user, 347)
        return redirect('seller-page', self.request.user.username)

    def test_func(self):
        is_allowed = False
        pk = self.kwargs['pk']
        post = get_object_or_404(Product, pk=pk)
        if self.request.user == post.user: 
            is_allowed = True
        return is_allowed

class SellerView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Product

    def get(self, *args, **kwargs):
        name = self.kwargs['name']
        allProds = []
        is_user = False
        user = User.objects.get(username=name)
        prods = Product.objects.filter(user__username=name).order_by('-pk')
        catprods = Product.objects.values('category', 'id')
        cats = {item['category'] for item in catprods}
        for cat in cats:
            prod = Product.objects.filter(category=cat, user__username=name)
            n = len(prod)
            nSlides = n // 4 + ceil((n / 4) - (n // 4))
            allProds.append([prod, range(1, nSlides), nSlides])
        if self.request.user == user:
            is_user = True
        params = {'allProds':allProds,
                    'prods': prods,
                    'is_user': is_user,
                    'len': len(prods)
                }
        return render(self.request, 'shop/seller.html', params)
    
    def test_func(self):
        name = self.kwargs['name']
        is_user = False
        user = User.objects.get(username__exact=name)
        seller_g = Group.objects.get(name='SELLER')
        if seller_g in self.request.user.groups.all() or self.request.user.is_superuser:
            is_user = True
        return is_user

class SellerShop(LoginRequiredMixin,UserPassesTestMixin, View):
    
    def get(self, *args, **kwargs):
        seller_group = Group.objects.get(name="SELLER")
        allProds = []
        catprods = Product.objects.values('category', 'id')
        cats = {item['category'] for item in catprods}
        for cat in cats:
            prod = Product.objects.filter(category=cat)
            n = len(prod)
            nSlides = n // 4 + ceil((n / 4) - (n // 4))
            allProds.append([prod, range(1, nSlides), nSlides])
        params = {'allProds':allProds}
        return render(self.request, 'shop/index.html', params)

    def test_func(self):
        # name = self.kwargs['name']
        is_user = False
        user = User.objects.get(username__exact=self.request.user.username)
        seller_g = Group.objects.get(name='SELLER')
        if seller_g in self.request.user.groups.all() or self.request.user.is_superuser:
            is_user = True
        return is_user

class OrderList(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        orders = Orders.objects.filter(user__exact=self.request.user).order_by('-pk')
        for order in orders:
            items = json.loads(order.items_json)

        params = {
            'orders':orders,
        }
        return render(self.request, 'shop/orderlist.html', params)

class OrderDetail(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        ref_code = kwargs['ref_code']
        items = [] 
        orders = Orders.objects.get(ref_code=ref_code)
        item = json.loads(orders.items_json)
        # items.append()
        print(list(item.values()), 423)
        print(items, 424)
        params = {
            # 'orders':orders,
            'items':list(item.values()) ,
        }
        return render(self.request, 'shop/orderdetail.html', params)

class SellerLogin(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'shop/seller_signin.html')
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            # Get the post parameters
            loginusername = request.POST['loginusername']
            loginpassword = request.POST['loginpassword']
            group = Group.objects.get(name="SELLER")
            user = authenticate(username=loginusername,
            password = loginpassword)
            if user is not None and group in user.groups.all():
                    login(request, user)
                    messages.success(request, "Successfully Logged In")
                    return redirect('ShopHome')
            else:
                messages.error(request, "Invalid Credentials, Plaese try again")
                return redirect('handleLogin')
        else: 
            return render(request, 'shop/seller_signin.html')