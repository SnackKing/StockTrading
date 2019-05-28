from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm, NewClassForm
from django.http import HttpResponse, JsonResponse
import pyrebase
import os
from django.contrib import messages
import json
import requests
import string
import random
from collections import OrderedDict


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
def landing(request):
	return render(request, 'teachers/landing.html')
def signout(request):
	del request.session['tid']
	del request.session['name']
	return redirect("teachers-landing")
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
			request.session['tid'] = userid
			name = teachers[userid]['name']
			request.session['name'] = name
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
			request.session['tid'] = userId
			request.session['name'] = username
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
	if 'tid' not in request.session:
		return redirect('teachers-login')
	#get user
	tid = request.session['tid']
	user = db.child('teachers').child(tid).get().val();
	classes = {}
	return render(request, 'teachers/dashboard.html', {'user': user, 'name':request.session['name']})

def newclass(request):
	if 'tid' not in request.session:
	 	return redirect('teachers-login')
	tid = request.session['tid']
	if request.method == "POST":
		form = NewClassForm(request.POST)
		if form.is_valid():
			className = form.cleaned_data.get('name')
			startingMoney = form.cleaned_data.get('startingCash')
			joinCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
			print(joinCode)
			db.child('teachers').child(tid).child('classes').child(joinCode).set({'className': className, 'startingMoney':startingMoney})
			db.child('codes_tid').child(joinCode).set(tid)
			messages.success(request, f'{className} class created')
			return redirect('teachers-dashboard')
		else:
			messages.error(request, 'Invalid Entry')
			return redirect('teachers-newclass')



	tid = request.session['tid']
	user = db.child('teachers').child(tid).get().val();
	form = NewClassForm()
	return render(request, 'teachers/newclass.html', {'form': form, 'user': user, 'name':request.session['name']})

def studentList(request, joinCode):
	if 'tid' not in request.session:
		return redirect('teachers-login')
	tid = request.session['tid']
	classData = db.child('teachers').child(tid).child('classes').child(joinCode).get().val();
	print(classData)
	return render(request, 'teachers/studentList.html', {'class': classData, 'joinCode': joinCode, 'name':request.session['name']})


def removeStudent(request, joinCode, studentId):
	tid = request.session['tid']
	db.child('teachers').child(tid).child('classes').child(joinCode).child('students').child(studentId).remove()
	print('Deleted')
	return redirect('teachers-class', joinCode = joinCode)

def deleteClass(request, joinCode):
	if 'tid' not in request.session:
		return redirect('teachers-login')
	tid = request.session['tid']
	db.child('teachers').child(tid).child('classes').child(joinCode).remove()
	db.child('codes_tid').child(joinCode).remove()
	messages.success(request, f'Class with join code {joinCode} deleted')
	return redirect('teachers-dashboard')

def account(request):
	if 'tid' not in request.session:
		return redirect('teachers-login')
	return render(request, 'teachers/account.html', {})

def leaderboard(request, joinCode):
	if 'tid' not in request.session:
		return redirect('teachers-login')
	tid = request.session['tid']
	students = db.child('teachers').child(tid).child('classes').child(joinCode).child('students').get().val()
	leaderboard = {}
	for studentId, name in students.items():
		studentVal = getPortfolioValue(studentId)
		leaderboard[studentId] = (studentVal, name)
	orderedKeys =sorted(leaderboard.keys(), key=lambda x: leaderboard[x][0], reverse = True)
	orderedLeaderboard = OrderedDict()
	for key in orderedKeys:
		orderedLeaderboard[key] = leaderboard[key]
	return render(request, 'teachers/leaderboard.html', {'leaderboard':orderedLeaderboard, 'name':request.session['name']})

def getPortfolioValue(studentId):
	user = db.child('users').child(studentId).get().val()
	portfolio = getOwnedEquity(user) if 'owned' in user else {}
	totalVal = sumAllAssets(user, portfolio)
	return totalVal
def getOwnedEquity(user):
    stocks = ""
    for stock in user['owned']:
        stocks += str(stock)
        stocks += ","
    #if at lease one stock was added, cut off extra trailing ','
    stocks = stocks[:-1] if stocks != "" else stocks
    print(stocks)
    parameters = {
        "token": 'sk_0a0d416a40b6401a87b46811783be7be', "symbols": stocks}
    response = requests.get(
        "https://cloud.iexapis.com/stable/tops", params=parameters)
    result = json.loads(response.content.decode('utf-8'))
    equitys = {}
    print("API RESULT")
    print(result)
    for item in result:
        equitys[item['symbol']] = round(float(item['lastSalePrice']) * int(user['owned'][item['symbol']]),2)
    return equitys

def sumAllAssets(user, equitys):
    stockVal = 0
    for stock in equitys:
        stockVal += equitys[stock]
    return user['balance'] + stockVal








 

 