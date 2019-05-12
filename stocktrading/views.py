from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import pyrebase
import os
from .forms import SignupForm, LoginForm
from django.contrib import messages
import json
import requests
from datetime import date, datetime, timedelta
from django.views.decorators.csrf import csrf_exempt


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

stockSample = [
    {
        'symbol': 'MSFT',
        'price': '100.0'
    },
    {
        'symbol': 'GOOG',
        'price': '1000.0'
    },
    {
        'symbol': 'GE',
        'price': '10.0'
    }


]


def home(request):
    uid = None
    if 'uid' in request.session:
        uid = request.session['uid']
    user = None;
    print('HOME UID')
    print(uid)
    if uid != None:
        user = db.child('users').child(uid).get().val();
    print(user);
    if(request.method == 'GET'):
        sym = request.GET.get('symbol', None)
        if sym != None:
            return redirect('stocktrading-stock', symbol=sym)
    stocks = "FB"
    if (user != None) and 'added' in user:
        stocks = ""
        for stock in user['added']:
            stocks += str(stock)
            stocks += ","
        stocks = stocks[:-1]
    print(stocks)
    parameters = {
        "api_token": 'mkUwgwc7TADeShHuZO7D2RRbeLu1b9PNd6Ptey0LkIeRliCUjdLJJB9UE4UX', "symbol": stocks}
    response = requests.get("https://www.worldtradingdata.com/api/v1/stock", params=parameters)
    result = json.loads(response.content.decode('utf-8'))
    data = result['data']
    ownedStocks = getOwnedStocks(data, user)
    print(ownedStocks)
    context = {
        'user': user,
        'uid': uid,
        'stocks': data,
        'owned': ownedStocks
    }
    return render(request, 'stocktrading/home.html', context)

def getOwnedStocks(data, user):
    owned = {}
    for item in data:
        if item['symbol'] in user['owned']:
            owned[item['symbol']] = item
    return owned

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
            request.session['uid'] = userid
            print("YOUR UID")
            print(request.session['uid'])
            user = db.child("users").child(userid).get()
            name = user.val()['name']
            messages.success(request, f'{name} has been logged in')
            return redirect('stocktrading-home')
    else:
        form = LoginForm()
        return render(request, 'stocktrading/login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # read in form data
            username = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # create user and sign them in
            auth.create_user_with_email_and_password(email, password)
            user = auth.sign_in_with_email_and_password(email, password)

            # get token and push related data
            newUser = {"name": username, "email": email, "balance":500}
            info = auth.get_account_info(user['idToken'])
            userInfo = info['users']
            userId = userInfo[0]['localId']
            request.session['uid'] = userId
            db.child("users").child(userId).set(newUser)

            # return flash message and redirect
            messages.success(request, f'Account created for {username}')
            return redirect('stocktrading-home')
    else:
        form = SignupForm()
        return render(request, 'stocktrading/signup.html', {'form': form})


def stocks(request, symbol):
    uid = None
    if 'uid' not in request.session:
        return redirect('stocktrading-home')
    uid = request.session['uid']
    parameters = {
        "api_token": 'mkUwgwc7TADeShHuZO7D2RRbeLu1b9PNd6Ptey0LkIeRliCUjdLJJB9UE4UX', "symbol": symbol}
    response = requests.get(
        "https://www.worldtradingdata.com/api/v1/stock", params=parameters)
    result = json.loads(response.content.decode('utf-8'))
    data = result['data'][0]
    today = datetime.today().strftime('%Y-%m-%d')
    earlier = datetime.today() - timedelta(days=7)
    earlier = earlier.strftime('%Y-%m-%d')
    historyParams = {"api_token": 'mkUwgwc7TADeShHuZO7D2RRbeLu1b9PNd6Ptey0LkIeRliCUjdLJJB9UE4UX',
                     'symbol': symbol, 'date_from': earlier, 'date_to': today, 'sort': 'oldest', 'output': 'json'}
    historyResponse = requests.get(
        "https://www.worldtradingdata.com/api/v1/history", params=historyParams)
    historyResult = json.loads(historyResponse.content.decode('utf-8'))
    filtered = historyResult['history']
    priceList = []
    dayList = []
    for day, stats in filtered.items():
        priceList.append(stats['close'])
        dayList.append(day)
    user = db.child("users").child(uid).get().val();
    owned = False;
    if ('owned' in user) and (symbol in user['owned']) and (user['owned'][symbol] != 0):
        owned = True
    numShares = 0
    if owned:
        numShares = user['owned'][symbol]

    print(user)
    context = {'symbol': symbol, 'stock': data, 'points': priceList, 'dayLabels': dayList, 'user': user, 'owned': owned, 'numShares': numShares}
    return render(request, 'stocktrading/stock.html', context)

@csrf_exempt
def add(request):
    symbol = request.POST.get("symbol")
    val = request.POST.get("value")
    uid = request.session['uid']
    newVal = ""
    if val == "Watch":
        db.child("users").child(uid).child("added").update({symbol: "doggo"})
        newVal = "Stop Watching"
    else:
        db.child("users").child(uid).child("added").child(symbol).remove()
        newVal = "Watch"
    data = {"newVal": newVal}
    return JsonResponse(data)

def buy(request,symbol):
    #number of shares that user entered
    count = request.POST.get("count")
    #hidden form element
    price = request.POST.get("price")
    uid = request.session['uid']
    user = db.child("users").child(uid).get().val();
    #update user balance
    newBalance = round(float(user['balance']) - (float(price) * float(count)),2)
    db.child("users").child(uid).update({'balance':newBalance})
    #update user stock count if they already own that stock, otherwise create new entry
    if ('owned' not in user) or (symbol not in user['owned']):
        db.child("users").child(uid).child("owned").update({symbol:count})
    else:
        owned = db.child("users").child(uid).child("owned").child(symbol).get().val();
        newCount = int(owned) + int(count);
        db.child("users").child(uid).child("owned").update({symbol: newCount})
    messages.success(request, f'You bought {count} shares of {symbol}')
    return redirect('stocktrading-stock', symbol = symbol)

def sell(request,symbol):
    #number of shares that user entered
    count = request.POST.get("count")
    #hidden form element
    price = request.POST.get("price")
    uid = request.session['uid']
    user = db.child("users").child(uid).get().val();
    #update user balance
    newBalance = round(float(user['balance']) + (float(price) * float(count)),2)
    db.child("users").child(uid).update({'balance':newBalance})
    #update user stock count if they already own that stock, otherwise create new entry
    if ('owned' not in user) or (symbol not in user['owned']):
        db.child("users").child(uid).child("owned").update({symbol:count})
    else:
        owned = db.child("users").child(uid).child("owned").child(symbol).get().val();
        newCount = int(owned) - int(count);
        db.child("users").child(uid).child("owned").update({symbol: newCount})
    messages.success(request, f'You sold {count} shares of {symbol}')
    return redirect('stocktrading-stock', symbol = symbol)
