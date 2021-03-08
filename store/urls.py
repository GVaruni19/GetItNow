from django.contrib import admin
from django.urls import path
from . import views
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.store, name='store'),
    # path('', views.store, name="home"),
    path('cart/', views.cart, name='cart'),
    path('register/', views.registerPage, name='register'),
    path('login', views.loginPage, name='login'),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
]

