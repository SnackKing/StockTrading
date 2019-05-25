from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm, NewClassForm
from django.http import HttpResponse, JsonResponse
import pyrebase
import os
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
db = firebase.database()
auth = firebase.auth()

# Create your views here.
def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			try:
				user = auth.sign_in_with_email_and_password(email, password)
			except:
				messages.error(request, 'No user exists with that username/password')
				return redirect('teachers-login')

			info = auth.get_account_info(user['idToken'])
			userid = info['users'][0]['localId']
			teachers = db.child("teachers").get().val();
			if userid not in teachers:
				messages.error(request, 'That account is not a teacher account')
				return redirect('teachers-login')
			request.session['uid'] = userid
			name = teachers[userid]['name']
			messages.success(request, f'{name} has been logged in')
			return redirect('teachers-dashboard')
	else:
		form = LoginForm()
		return render(request, 'teachers/login.html', {'form': form, 'user':None})

def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			# read in form data
			username = form.cleaned_data.get('name')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			joinCode = form.cleaned_data.get('code')

			# create user and sign them in
			auth.create_user_with_email_and_password(email, password)
			user = auth.sign_in_with_email_and_password(email, password)

			# get token and push related data
			newUser = {"name": username, "email": email}
			info = auth.get_account_info(user['idToken'])
			userInfo = info['users']
			userId = userInfo[0]['localId']
			request.session['uid'] = userId
			db.child("teachers").child(userId).set(newUser)

			# return flash message and redirect
			messages.success(request, f'Account created for {username}')
			return redirect('teachers-dashboard')
		else:
			messages.error(request, 'Invalid Entry')
			return redirect('teachers-signup')
	else:
		form = SignupForm()
		return render(request, 'teachers/signup.html', {'form': form, 'user':None})

def dashboard(request):
	if 'uid' not in request.session:
		return redirect('teachers-login')
	#get user
	uid = request.session['uid']
	user = db.child('teachers').child(uid).get().val();
	classes = {}
	return render(request, 'teachers/dashboard.html', {'user': user})

def newclass(request):
	if 'uid' not in request.session:
	 	return redirect('teachers-login')
	#get user
	uid = request.session['uid']
	user = db.child('teachers').child(uid).get().val();
	form = NewClassForm()
	return render(request, 'teachers/newclass.html', {'form': form, 'user': user})



 

 