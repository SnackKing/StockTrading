from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyrebase
import os
from .forms import SignupForm, LoginForm
from django.contrib import messages
import json
import requests

config = {
  "apiKey": "AIzaSyAzXh-si71dEDldZkLmbY7l-_NZ8VJTfs4",
  "authDomain": "stocktrader-239615.firebaseapp.com",
  "databaseURL":  "https://stocktrader-239615.firebaseio.com",
  "storageBucket": "stocktrader-239615.appspot.com",
  "serviceAccount": "creds.json"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database();
auth = firebase.auth()
# Create your views here.

stockSample = [
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
	if(request.method == 'GET'):
		print("GEt fuuuuuucked")
		sym = request.GET.get('symbol', None)
		if sym != None:
			print(sym)
			return redirect('stocktrading-stock', symbol = sym)

	context ={
		'stocks': stockSample
	}
	parameters = {"api_token": 'mkUwgwc7TADeShHuZO7D2RRbeLu1b9PNd6Ptey0LkIeRliCUjdLJJB9UE4UX' , "symbol": 'AAPL'}
	#response = requests.get("https://www.worldtradingdata.com/api/v1/stock", params=parameters)
	#result = json.loads(response.content.decode('utf-8'))
	#data = result['data'][0]['symbol'];
	#print(data)
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
			password = form.cleaned_data.get('password')
			user = auth.sign_in_with_email_and_password(email, password)
			info = auth.get_account_info(user['idToken'])
			userid = info['users'][0]['localId']
			user = db.child("users").child(userid).get();
			name = user.val()['name']
			messages.success(request, f'{name} has been logged in')
			return redirect('stocktrading-home')
	else:
		form = LoginForm()
		return render(request, 'stocktrading/login.html', {'form':form})


def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			#read in form data
			username = form.cleaned_data.get('name')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')

			#create user and sign them in
			auth.create_user_with_email_and_password(email, password)
			user = auth.sign_in_with_email_and_password(email, password)

			#get token and push related data
			newUser = {"name": username, "email": email}
			info = auth.get_account_info(user['idToken'])
			userInfo = info['users']
			userId = userInfo[0]['localId']
			db.child("users").child(userId).set(newUser);


			#return flash message and redirect
			messages.success(request, f'Account created for {username}')
			return redirect('stocktrading-home')
	else:
		form = SignupForm()
		return render(request, 'stocktrading/signup.html', {'form':form})

def stocks(request, symbol):
	parameters = {"api_token": 'mkUwgwc7TADeShHuZO7D2RRbeLu1b9PNd6Ptey0LkIeRliCUjdLJJB9UE4UX' , "symbol": symbol}
	response = requests.get("https://www.worldtradingdata.com/api/v1/stock", params=parameters)
	result = json.loads(response.content.decode('utf-8'))
	data = result['data'][0]
	stuff = [5,2,4,5,3];
	context = {'symbol': data['symbol'], 'price': data['price'], 'name': data['name'], 'currency': data['currency'], 'day_high': data['day_high'], 'day-low': data['day_low'], 'day_change': data['day_change'], 'change_pct': data['change_pct'], 'points':stuff}
	return render(request, 'stocktrading/stock.html', context)


