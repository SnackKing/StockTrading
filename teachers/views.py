from django.shortcuts import render
from .forms import SignupForm, LoginForm


# Create your views here.
def login(request):
    form = LoginForm()
    return render(request, 'stocktrading/login.html', {'form': form, 'user':None})

 