from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('regist', views.registUser, name='regist_user')
]