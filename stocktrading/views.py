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
import collections
from collections import OrderedDict
import random



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

def splitStocks(stocks):
    result = []
    stockList = stocks.split(",")
    for x in range(0, len(stockList),5):
        result.append(",".join(stockList[x:x+5]))
    return result


def home(request):
    #redirect user if they arent signed in
    if 'uid' not in request.session:
        return redirect('stocktrading-landing')

    #get user
    uid = request.session['uid']
    user = db.child('users').child(uid).get().val();

    #search bar query, redirect to stock page with given symbol
    if(request.method == 'GET'):
        sym = request.GET.get('symbol', None)
        if sym != None:
            return redirect('stocktrading-stock', symbol=sym)
    stocks = ""
    seenStocks = set()
    #get all owned and tracked stocks
    if 'added' in user:
        stocks = ""
        #get all tracked stocks
        for stock in user['added']:
            if stock not in seenStocks:
                seenStocks.add(stock)
                stocks += str(stock)
                stocks += ","
    #get all owned stocks
    if 'owned' in user:
        for stock in user['owned']:
            if stock not in seenStocks:
                seenStocks.add(stock)
                stocks += str(stock)
                stocks += ","

    #if at lease one stock was added, cut off extra trailing ','
    stocks = stocks[:-1] if stocks != "" else stocks
    stockList = splitStocks(stocks)
    #if the user had at least one stock, then make an api call for the requested stocks
    data = []
    if stocks != "":
        for group in stockList:
            parameters = {
                "api_token": randomKey(), "symbol": group}
            response = requests.get("https://www.worldtradingdata.com/api/v1/stock", params=parameters)
            result = json.loads(response.content.decode('utf-8'))
            data = data + result['data']
    #get all stocks that are owned so that they can be displayed properly on the home page
    ownedStocks = getOwnedStocks(data, user)
    watchedStocks = getWatchedStocks(data,user)
    context = {
        'user': user,
        'uid': uid,
        'stocks': data,
        'watched': watchedStocks,
        'owned': ownedStocks,

    }
    return render(request, 'stocktrading/home.html', context)

def getOwnedStocks(data, user):
    owned = {}
    for item in data:
        if ('owned' in user) and (item['symbol'] in user['owned']):
            owned[item['symbol']] = item
            temp = owned[item['symbol']]
            temp['numShares'] = user['owned'][item['symbol']]
    return owned

def getWatchedStocks(data, user):
    watched = {}
    for item in data:
        if ('added' in user) and (item['symbol'] in user['added']):
            watched[item['symbol']] = item
    return watched

def about(request):
    #redirect if not signed in
    if "uid" not in request.session:
        return redirect('stocktrading-login')
    #get user
    uid = request.session['uid']
    user = db.child('users').child(uid).get().val();
    context = {
    'user':user
    }
    return render(request, 'stocktrading/about.html', context)


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
                return redirect('stocktrading-login')

            info = auth.get_account_info(user['idToken'])
            userid = info['users'][0]['localId']
            request.session['uid'] = userid
            user = db.child("users").child(userid).get()
            name = user.val()['name']
            messages.success(request, f'{name} has been logged in')
            return redirect('stocktrading-home')
        else:
            messages.error(request, 'Invalid Entry')
            return redirect('stocktrading-login')

    else:
        form = LoginForm()
        return render(request, 'stocktrading/login.html', {'form': form, 'user':None})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # read in form data
            username = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            code = form.cleaned_data.get('code')
            print(code)
           
            # create user and sign them in
            auth.create_user_with_email_and_password(email, password)
            user = auth.sign_in_with_email_and_password(email, password)

            # get token and push related data
            newUser = {"name": username, "email": email, "balance":500}
            info = auth.get_account_info(user['idToken'])
            userInfo = info['users']
            userId = userInfo[0]['localId']
            request.session['uid'] = userId
            #get class info if join code used
            if not code == None:
                tid = db.child('codes_tid').child(code).get().val();
                print(tid);
                if not tid == None:
                    classInfo = db.child('teachers').child(tid).child('classes').child(code).get().val()
                    print(classInfo)
                    newUser['balance'] = int(classInfo['startingMoney'])
                    newUser['className'] = classInfo['className']
                    db.child('teachers').child(tid).child('classes').child(code).child('students').child(userId).set(username)

            db.child("users").child(userId).set(newUser)

            # return flash message and redirect
            messages.success(request, f'Account created for {username}')
            return redirect('stocktrading-home')
        else:
            messages.error(request, 'Invalid Entry')
            return redirect('stocktrading-signup')


    else:
        form = SignupForm()
        return render(request, 'stocktrading/signup.html', {'form': form, 'user':None})


def stocks(request, symbol):
    #redirect user if they arent signed in
    uid = None
    if 'uid' not in request.session:
        return redirect('stocktrading-home')
    uid = request.session['uid']

    #make API call to get data for stock in question
    parameters = {
        "api_token": randomKey(), "symbol": symbol}
    response = requests.get(
        "https://www.worldtradingdata.com/api/v1/stock", params=parameters)
    result = json.loads(response.content.decode('utf-8'))

    #if no data attribute, then user entered an invalid symbol. Redirect to home with flash message
    if 'data' not in result:
        messages.error(request, f'{symbol} is not a valid symbol')
        return redirect('stocktrading-home')

    data = result['data'][0]

    #create date object for today and 1 week ago for API call
    today = datetime.today().strftime('%Y-%m-%d')
    earlier = datetime.today() - timedelta(days=7)
    earlier = earlier.strftime('%Y-%m-%d')

    #make api call for historical price data for stock
    historyParams = {"api_token": randomKey(),
                     'symbol': symbol, 'date_from': earlier, 'date_to': today, 'sort': 'oldest', 'output': 'json'}
    historyResponse = requests.get(
        "https://www.worldtradingdata.com/api/v1/history", params=historyParams)
    historyResult = json.loads(historyResponse.content.decode('utf-8'))
    filtered = historyResult['history']

    #parse results into labels and points for chart.js
    priceList = []
    dayList = []
    for day, stats in filtered.items():
        priceList.append(stats['close'])
        dayList.append(day)

    user = db.child("users").child(uid).get().val();

    #figure out if user actually owns this stock
    owned = False;
    if ('owned' in user) and (symbol in user['owned']) and (user['owned'][symbol] != 0):
        owned = True

    #get additonal user data to display  
    numShares = 0
    returnVal = 0
    numTrans = 0
    totalreturn = 0
    equity = 0
    if owned:
        numShares = user['owned'][symbol]
        equity = round(int(numShares) * float(data['price']),2)
        cost = db.child("users").child(uid).child("return").child(symbol).get().val();
        returnVal = round(float(cost) + equity,2)

    #get historical ownership data for this stock for this user. This must be separate from the previous block becasue the user not owning
    #the stock right now does not imply that the user has not owned the stock in the past
    try:
        numTrans = user['stats']['transCount'][symbol]
        totalreturn = round(float(user['stats']['totalreturn'][symbol]) + (float(data['price'])*int(numShares)),2)
    except KeyError:
        pass
    newsData = getNewsData(symbol)
    context = {'symbol': symbol, 'stock': data, 'points': priceList, 'dayLabels': dayList, 'user': user, 'owned': owned, 'numShares': numShares, 'equity': equity, 'returnVal': returnVal, 'numTrans':numTrans, 'totalReturn':totalreturn, 'newsData':newsData}
    return render(request, 'stocktrading/stock.html', context)

def getNewsData(symbol):
    parameters = {"token": "3rnk49qveukvizaifh0bykco6o3ogpfiiamqimvy", "tickers": symbol,'type':'article', 'items':"5", 'fallback':"true"}
    response = requests.get("https://stocknewsapi.com/api/v1", params=parameters)
    newsResult = json.loads(response.content.decode('utf-8'))
    newsData = newsResult['data'];
    print(type(newsData))
    return newsData


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

    #get user
    uid = request.session['uid']
    user = db.child("users").child(uid).get().val();

    #update user balance
    newBalance = round(float(user['balance']) - (float(price) * float(count)),2)
    db.child("users").child(uid).update({'balance':newBalance})

    #update user stock count if they already own that stock, otherwise create new entry
    increaseOwnedAndCost(symbol,count, price,user,uid)

    #add buy order to user's history
    addBuyOrder(count, price, user, symbol, uid)

    #increment total number of transactions made for this stock for this user
    increaseTransactionCount(symbol, count, uid,user)

    #update total return for this stock
    updateReturn(symbol, float(price)*int(count)*-1, uid)

    #create success message for stock being bought
    messages.success(request, f'You bought {count} shares of {symbol}')
    return redirect('stocktrading-stock', symbol = symbol)

def increaseOwnedAndCost(symbol, count,price,user,uid):
    #if stock isnt owned, then create field for stock in owned and return tables
    if ('owned' not in user) or (symbol not in user['owned']):
        db.child("users").child(uid).child("owned").update({symbol:count})
        db.child("users").child(uid).child("return").update({symbol: (float(price) * float(count)*-1)})
    else:
        #if stock is owned, add to already existing values
        #values for number of owned stocks
        curOwned = db.child("users").child(uid).child("owned").child(symbol).get().val();
        newCount = int(curOwned) + int(count);
        db.child("users").child(uid).child("owned").update({symbol: newCount})

        #values for current return of stock
        curCost = db.child("users").child(uid).child("return").child(symbol).get().val()
        newCost =float(curCost) - (float(price) * int(count))
        db.child("users").child(uid).child("return").update({symbol:newCost})


def sell(request,symbol):
    #number of shares that user entered
    count = request.POST.get("count")

    #hidden form element
    price = request.POST.get("price")

    #get user
    uid = request.session['uid']
    user = db.child("users").child(uid).get().val();

    #update user balance
    newBalance = round(float(user['balance']) + (float(price) * float(count)),2)
    db.child("users").child(uid).update({'balance':newBalance})

    #update user stock count if they already own that stock, otherwise create new entry
    decreaseOwnedAndCost(symbol, count,price,user,uid)

    #add order to user's history
    addSellOrder(count,price,user,symbol,uid)

    #increment total number of transactions made for the stock for this user
    increaseTransactionCount(symbol, count, uid,user)

    #update total return for this stock for this user
    updateReturn(symbol, float(price)*int(count),uid)

    #flash message for success
    messages.success(request, f'You sold {count} shares of {symbol}')
    return redirect('stocktrading-stock', symbol = symbol)

def decreaseOwnedAndCost(symbol, count, price,user,uid):
    #if stock is being sold, then we can assume that the user had to have owned it in the first place, which means that owned and return fields must exit
    owned = db.child("users").child(uid).child("owned").child(symbol).get().val();
    curCost = db.child("users").child(uid).child("return").child(symbol).get().val()
    newCost = float(curCost) + (float(price) * int(count))
    db.child("users").child(uid).child("return").update({symbol: newCost})
    newCount = int(owned) - int(count);
    db.child("users").child(uid).child("owned").update({symbol: newCount})
    #if user no longer owns any share, remove temporary fields entirely
    if newCount == 0:
        db.child("users").child(uid).child("owned").child(symbol).remove()
        db.child("users").child(uid).child("return").child(symbol).remove()

def increaseTransactionCount(symbol, numShares,uid, user):
    #add number of shares bought to current total amount of shares bought/sold of the stock
    numTrans = db.child("users").child(uid).child("stats").child("transCount").child(symbol).get().val();
    if numTrans is None:
        numTrans = 0;
    newNum = int(numTrans) + int(numShares)
    db.child("users").child(uid).child("stats").child("transCount").update({symbol:newNum})

def updateReturn(symbol, amount, uid):
    totalReturn = db.child("users").child(uid).child("stats").child("totalreturn").child(symbol).get().val()
    if totalReturn is None:
        totalReturn = 0
    newTotal = float(totalReturn) + amount
    db.child("users").child(uid).child("stats").child("totalreturn").update({symbol: newTotal })

def landing(request):
    return render(request, 'stocktrading/landing.html', {'user': None})

#creates a new buy order in the database with timestamp, symbol, number of shares, and price bought at
def addBuyOrder(count, price, user, symbol,uid):
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    db.child("users").child(uid).child('orders').child('buy').child(timestamp).set({'symbol':symbol, 'numShares': count, 'price': price})

#creates a new sell order in the database with timestamp, symbol, number of shares, and price sold at
def addSellOrder(count, price, user, symbol,uid):
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    db.child("users").child(uid).child('orders').child('sell').child(timestamp).set({'symbol':symbol, 'numShares': count, 'price': price})

def account(request):
    uid = request.session['uid']
    user = db.child('users').child(uid).get().val();
    topStocks = {}
    if "stats" in user:
        trans = user["stats"]["transCount"]
       # topStocks = OrderedDict(sorted(trans.items(), key = lambda t: t[1], reverse = True))
        topStocks = dict(collections.Counter(trans).most_common(5))
    equities = getOwnedEquity(user) if "owned" in user else {}
    totalValue = round(sumAllAssets(user,equities),2)
    return render(request, 'stocktrading/account.html', {'user': user, 'favs': topStocks, 'equities': equities, 'total': totalValue})

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
    print(result)
    for item in result:
        equitys[item['symbol']] = round(float(item['lastSalePrice']) * int(user['owned'][item['symbol']]),2)
    return equitys

def sumAllAssets(user, equitys):
    stockVal = 0
    for stock in equitys:
        stockVal += equitys[stock]
    return user['balance'] + stockVal

def transactions(request):
    if 'uid' not in request.session:
        return redirect('stocktrading-landing')
    uid = request.session['uid']
    user = db.child('users').child(uid).get().val();
    transactions = {};
    if 'orders' in user:
        buys = {}
        if 'buy' in user['orders']:
            for key, value in user['orders']['buy'].items():
                buys[key] = value
            newBuys = OrderedDict(sorted(buys.items(), reverse = True))
            transactions["buys"] = newBuys
        if 'sell' in user['orders']:
            sells = {}
            for key,value in user['orders']['sell'].items():
                sells[key] = value
            newSells = OrderedDict(sorted(sells.items(), reverse = True))
            transactions["sells"] = newSells;


    return render(request, 'stocktrading/transactions.html', {'transactions': transactions, 'user': user})

def signout(request):
    del request.session['uid']
    return redirect("stocktrading-landing")

#Using 2 API keys because why not
def randomKey():
    rdmBool = bool(random.getrandbits(1))
    if rdmBool:
        return "o3yCTA0mVXrkep8zrRwmL2vt6kPJ8KPgZdbF6D8whZNDRkGqAteM3TewEAsK"
    else:
        return "mkUwgwc7TADeShHuZO7D2RRbeLu1b9PNd6Ptey0LkIeRliCUjdLJJB9UE4UX"

