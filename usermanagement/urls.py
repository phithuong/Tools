from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('regist', views.regist_user, name='regist_user')
]