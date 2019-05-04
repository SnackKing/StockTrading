from django.shortcuts import render
from django.http import HttpResponse
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
	context ={
		'stocks': stocks
	}
	return render(request, 'stocktrading/home.html', context) #template subdirname/filename format

def about(request):
	return render(request, 'stocktrading/about.html')
