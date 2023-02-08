from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    
    path('', views.loginPage,name='login1'),
    path('index', views.index,name='home'),
    path('team', views.team,name='team'),
    path('design', views.design,name='design'),
    path('push', views.push,name='push'),
    path('register/',views.registerPage,name='register'),
    path('login1/',views.loginPage,name='login1'),
    path('logout/',views.logoutUser,name='logout'),
    #path('homes/',views.Home,name='Home'),
    path('speed/',views.vehicle_speed,name='Speed')
]