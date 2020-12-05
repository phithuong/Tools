from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('add_cart/', views.add_cart, name='add_cart'),
    path('remove_cart/', views.remove_cart, name='remove_cart'),
    path('search/<p>', views.home, name='home'),
]
