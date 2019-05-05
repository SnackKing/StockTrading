from django.shortcuts import render
from django.http import HttpResponse
import pyrebase
import os
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
	db.child("agents").set(archer)
	context ={
		'stocks': stocks
	}
	return render(request, 'stocktrading/home.html', context) #template subdirname/filename format

def about(request):
	context = {
	}
	return render(request, 'stocktrading/about.html', context)

def login(request):
	context = {
	}
	return render(request, 'stocktrading/login.html', context)

def signup(request):
	context = {
	}
	return render(request, 'stocktrading/signup.html', context)
