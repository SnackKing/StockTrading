from django.urls import path
from . import views
urlpatterns = [
    path('dashboard/', views.dashboard, name ='teachers-dashboard'),
    path('login/', views.login, name = 'teachers-login'),
    path('signup/', views.signup, name = 'teachers-signup'),
    path('newclass/', views.newclass, name = 'teachers-newclass'),
    path('dashboard/classes/<str:joinCode>/', views.studentList, name = 'teachers-class'),

  

]
