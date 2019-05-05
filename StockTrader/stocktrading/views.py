from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyrebase
import os
from .forms import SignupForm, LoginForm
from django.contrib import messages

config = {
  "apiKey": "AIzaSyAzXh-si71dEDldZkLmbY7l-_NZ8VJTfs4",
  "authDomain": "stocktrader-239615.firebaseapp.com",
  "databaseURL":  "https://stocktrader-239615.firebaseio.com",
  "storageBucket": "stocktrader-239615.appspot.com",
  "serviceAccount": "creds.json"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database();
# Create your views here.

stocks = [
	{
		'symbol':'MSFT',
		'price':'100.0'
	},
	{
		'symbol':'GOOG',
		'price':'1000.0'
	},
	{
		'symbol':'GE',
		'price':'10.0'
	}

	
]

def home(request):
	archer = {"name": "Sterling Archer", "agency": "Figgis Agency"}
	#db.child("agents").set(archer)
	context ={
		'stocks': stocks
	}
	return render(request, 'stocktrading/home.html', context) #template subdirname/filename format

def about(request):
	context = {
	}
	return render(request, 'stocktrading/about.html', context)

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			messages.success(request, f'{email} has been logged in')
			return redirect('stocktrading-home')
	else:
		form = LoginForm()
		return render(request, 'stocktrading/login.html', {'form':form})


def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('name')
			messages.success(request, f'Account created for {username}')
			return redirect('stocktrading-home')
	else:
		form = SignupForm()
		return render(request, 'stocktrading/signup.html', {'form':form})
