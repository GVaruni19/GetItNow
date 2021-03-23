from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm

# Create your views here.

def registerPage(request):
    form = CreateUserForm()

    if request.method=="POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            Customer.objects.create(user=user, name=username, email=user.email)
            messages.success(request, "Account created successfully for "+username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'store/registration.html', context)


def loginPage(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')        
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged In")
            return redirect('store')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect("login")

    context = {}
    return render(request, 'store/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect("/")


def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    cat_menu = Category.objects.all()
    context = {'products':products, 'cartItems':cartItems, 'cat_menu':cat_menu}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    cat_menu = Category.objects.all()

    context = {'items':items, 'order':order, 'cartItems':cartItems, 'cat_menu':cat_menu}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    cat_menu = Category.objects.all()

    context ={'items' :items, 'order': order, 'cartItems' :cartItems, 'cat_menu':cat_menu}
    return render(request, 'store/checkout.html',context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action: ',action)
    print('productId: ',productId)

    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = request.user.customer, complete= False)

    orderItem, created = OrderItem.objects.get_or_create(order= order, product= product)

    if action=='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove' :
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('item added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if(request.user.is_authenticated):
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer)

    else:
        customer, order = guestOrder(request, data)    

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total==float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )   

    return JsonResponse('Payment complete!', safe=False)


def CategoryView(request, cats):
    data = cartData(request)
    cartItems = data['cartItems']
    category_products = Product.objects.filter(category = cats.replace('-', ' '))
    cat_menu = Category.objects.all()

    context = {'cats':cats.title().replace('-', ' '), 'category_products':category_products, 'cat_menu':cat_menu, 'cartItems':cartItems}
    return render(request, 'store/categories.html', context )

def CategoryListView(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    cat_menu_list = Category.objects.all()
    return render(request, 'store/category_list.html', {'cat_menu_list': cat_menu_list, 'cartItems':cartItems})