from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('fb_login', views.fb_login, name='fb_login'),
    path('fb_logout', views.fb_logout, name='fb_logout'),
    path('regist', views.regist_user, name='regist_user'),
]