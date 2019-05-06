from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name ='stocktrading-home'),
    path('about/', views.about, name ='stocktrading-about'),
    path('login/', views.login, name = 'stocktrading-login'),
    path('signup/', views.signup, name = 'stocktrading-signup'),
    path('stocks/<str:symbol>/', views.stocks, name = 'stocktrading-stock')

]
