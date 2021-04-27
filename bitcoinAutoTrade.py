import time
import pyupbit
import datetime
import requests

access = "mGtkK4oHuRzC87HhFq8DYXgZr5HgGzkbHrNJdO36"
secret = "j4DprBWHAeLxqfQ33Y4ivhSOoAWBBJAdSqKCrtRa"
myToken = "xoxb-1997441711206-2001145216773-XJvBmeSqwWfvVrkFtLPQ2c46"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2) 
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1) # 일봉으로 조회하면 그날의 시작 시간이 나온다.
    start_time = df.index[0]  # 시간값.
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#-ai", "start")

while True:
    try:
        now = datetime.datetime.now() # 현재시간
        start_time = get_start_time("KRW-ETH") # 시작시간 
        end_time = start_time + datetime.timedelta(days=1) # 끝나는 시간. ( 다음날 9 시)

        if start_time < now < end_time - datetime.timedelta(seconds=10): # 8시 59분 50초까지 돌아가게한다. // # 9시 < 현재 < 8시 59 : 50
            target_price = get_target_price("KRW-ETH", 0.5) # 변동성 돌파전략으로 목표가를 정하고
            ma15 = get_ma15("KRW-ETH")
            current_price = get_current_price("KRW-ETH") # 현재 가격 조회
            if target_price < current_price and ma15 < current_price: # 이동 평균선도 확인한다.
                krw = get_balance("KRW") 
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-ETH", krw*0.9995) # 비트코인을 매수한다. 이때 수수료 0.05 % 를 고려한다.
                    post_message(myToken,"#-ai", "ETH buy : " +str(buy_result))
        else: # 10초전일떄는
            ETH = get_balance("ETH")
            if ETH > 0.00008:
                sell_result = upbit.sell_market_order("KRW-ETH", ETH*0.9995)
                post_message(myToken,"#-ai", "ETH buy : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#-ai", e)
        time.sleep(1)