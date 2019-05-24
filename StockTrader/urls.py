"""StockTrader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from teachers import views as teacher_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stocktrading.urls')),
    path('teachers/login', teacher_views.login, name ='teachers-login'),
    path('teachers/signup', teacher_views.signup, name='teachers-signup'),
    path('teachers/dashboard', teacher_views.dashboard, name = 'teachers-dashboard'),
]
