from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('8suvXUHjBNey25GGX1kvuip5RM2vNUyIxEgMqZVJYKW7cJuS3qKd9edtw5Y5s3UATnrdfEMjj3r/69SiztrtIcWLdqWpGmsIwmYIhAUGvdDbqOxzMiWmywaQMgSFbCb/ewJA0v2581gHdU/ZfK4OBAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b6b6b707c23e48e6b8f3b588ffdc3146')

#there is my code

def getTWSEdata(stockCode="1301", monthDate="20170801"):
    # monthDate = 20170801
    import requests
    import pickle
    import os
    import json
    r = requests.get('http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}'.format(monthDate,stockCode))
    #print('http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}'.format(monthDate,stockCode))
    data = json.loads(r.text)
    prices = data['data']
    return prices
    #"��̖  ���Q ����       �ɽ��ɔ�   �ɽ����~     �_�P�r ���߃r ���̓r �ձP�r �q���� �ɽ��P��"

def getThisMonth(daysAgo=31):
    from datetime import datetime, date, time, timedelta
    today = datetime.today()
    first = today.replace(day=1)
    lastMonth = first - timedelta(days=daysAgo)
    dateStr = lastMonth.strftime("%Y%m01")
    return dateStr

def moving_average(x, n, type='simple'):
    from numpy import array
    import numpy as np
    #compute an n period moving average.
    #type is 'simple' | 'exponential'
    x = np.asarray(x)
    if type == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))
    weights /= weights.sum()
    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

def moving_average_convergence(x, nslow=26, nfast=12):
    from numpy import array
    import numpy as np
    #compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    #return value is emaslow, emafast, macd which are len(x) arrays
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    return emaslow, emafast, emafast - emaslow

def relative_strength(prices, n=14):
    from numpy import array
    import numpy as np
    #compute the n period relative strength indicator
    #http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
    #http://www.investopedia.com/terms/r/rsi.asp
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)
    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(n - 1) + upval)/n
        down = (down*(n - 1) + downval)/n
        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)
    return rsi

def getTA(fh, nslow=20, nfast=5, nema=10):
    from numpy import array
    import numpy as np
    fh = array(fh)
    prices = fh.astype(np.float) # Price from Str to float
    emaslow, emafast, macd = moving_average_convergence(prices, nslow=nslow, nfast=nfast)
    rsi = relative_strength(prices) # RSI
    revMACD = list(reversed(macd))
    revRSI = list(reversed(rsi))
    revDalist = list(reversed(fh))
    dalistTA = []
    for i in range(len(fh)):
        dalistTA.append([fh[i],revMACD[i],revRSI[i]])
    reversed(dalistTA)
    return dalistTA

def predictAnswer(code,file,thresh=0.5):
    import xgboost as xgb
    nameofMODEL = 'data5day'+str(code)+'.model'
    bst = xgb.Booster({'nthread': 4})
    bst.load_model(nameofMODEL)
    dtest = xgb.DMatrix(file)
    preds = bst.predict(dtest)
    return preds

def getPred(code):
    dateStr = getThisMonth(331)
    prices = getTWSEdata(stockCode=code, monthDate=dateStr)
    dateStr = getThisMonth(301)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(271)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(241)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(211)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(181)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(151)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(121)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(91)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(61)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(31)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    dateStr = getThisMonth(0)
    prices.extend(getTWSEdata(stockCode=code, monthDate=dateStr))
    CloseList = []
    predictions = []
    for i,val in enumerate(prices):
        CloseList.append(prices[i][6])
    dalistTA = getTA(CloseList, nslow=20, nfast=5, nema=10)
    for i,val in enumerate(dalistTA):
        dtest = "1:"+str(dalistTA[i][0])+" 2:"+str(dalistTA[i][1])+" 3:"+str(dalistTA[i][2])+'\n'
        with open('temp.csv', 'w') as f:
            f.write(dtest)
        preds = predictAnswer(code,'temp.csv')
        #print(i," ",preds," ",dalistTA[i][0])
        predictions.append(preds)
    #print("Average:",sum(predictions)/float(len(predictions)),"")
    avgpred = sum(predictions)/float(len(predictions))
    avgli = [avgpred] * len(predictions)
    
    import matplotlib
    import numpy as np
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.plot(predictions)
    plt.plot(avgli)
    plt.savefig('Pred.png')
    
    


#there is my code


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = getPred(int(event.message.text)))) #event.message.text


if __name__ == "__main__":
    app.run()
