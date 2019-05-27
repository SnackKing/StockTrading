from django.urls import path
from . import views
urlpatterns = [
    path('dashboard/', views.dashboard, name ='teachers-dashboard'),
    path('login/', views.login, name = 'teachers-login'),
    path('signup/', views.signup, name = 'teachers-signup'),
    path('account/', views.account, name = 'teachers-account'),
    path('newclass/', views.newclass, name = 'teachers-newclass'),
    path('dashboard/classes/<str:joinCode>/', views.studentList, name = 'teachers-class'),
    path('dashboard/classes/<str:joinCode>/leaderboard/', views.leaderboard, name = 'teachers-leaderboard'),
    path('dashboard/classes/<str:joinCode>/removestudent/<str:studentId>', views.removeStudent, name = 'teachers-removeStudent'),
    path('dashboard/classes/<str:joinCode>/deleteclass', views.deleteClass, name = 'teachers-deleteclass'),


  

]
