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

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products' : products, 'cartItems' :cartItems}
    return render(request, 'store/store.html',context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context ={'items' :items, 'order': order, 'cartItems' :cartItems}
    return render(request, 'store/cart.html',context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context ={'items' :items, 'order': order, 'cartItems' :cartItems}
    return render(request, 'store/checkout.html',context)


def updateItem(request, customer):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action: ',action)
    print('productId: ',productId)

    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer, complete= False)

    orderItem, created = OrderItem.objects.get_or_create(order= order, product= product)

    if action=='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove' :
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('item added', safe=False)


def processOrder(request, customer):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if(request.user.is_authenticated):
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete= False)

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


def registerPage(request):
    form = CreateUserForm()

    if request.method=="POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, "Account created successfully for "+user)
            return redirect('login')

    context = {'form': form}
    return render(request, 'store/registration.html', context)

    # if request.method=="POST":
    #     mail=request.POST.get('email', '')
    #     first_name=request.POST.get('firstname', '')
    #     last_name=request.POST.get('lastname', '')
    #     username=request.POST.get('username', '')
    #     password=request.POST.get('password', '')
    #     confirmpassword=request.POST.get('confirmpassword', '')
    #     userCheck=User.objects.filter(username=username) | User.objects.filter(email=mail)
    #     if userCheck:
    #         print('iamhere')
    #         messages.error(request, "Username or Email already exists!")
    #         return redirect("register")
    #     else:
    #         if password==confirmpassword:
    #             user_obj=User.objects.create_user(first_name=first_name, last_name=last_name, password=password, email=mail, username=username)
    #             user_obj.save()
    #             messages.success(request, "Signed Up successfully")
    #             return redirect("store")
    #         else:
    #             messages.error(request, "Passwords don't match!")
    #             print('hi')
    #             return redirect("register")
    # return render(request, 'store/registration.html')


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