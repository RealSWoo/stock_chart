import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import pandas as pd

# 기간 설정
start_date = '2008-01-01'
end_date   = '2018-12-31'

# 지수 데이터 가져오기
df_kospi = fdr.DataReader('KS11', start_date, end_date)
df_kosdaq = fdr.DataReader('KQ11', start_date, end_date)
df_usdkrw = fdr.DataReader('USD/KRW', start_date, end_date)
df_dow = fdr.DataReader('DJI', start_date, end_date)
df_nasdaq = fdr.DataReader('IXIC', start_date, end_date)

# 정규화: 시작일 대비 100으로 변환
kospi_norm = df_kospi['Close'] / df_kospi['Close'].iloc[0] * 100
kosdaq_norm = df_kosdaq['Close'] / df_kosdaq['Close'].iloc[0] * 100
usdkrw_norm = df_usdkrw['Close'] / df_usdkrw['Close'].iloc[0] * 100
dow_norm = df_dow['Close'] / df_dow['Close'].iloc[0] * 100
nasdaq_norm = df_nasdaq['Close'] / df_nasdaq['Close'].iloc[0] * 100

# 시작일 정보 확인
start_date_kospi = df_kospi.index[0].date()
start_price_kospi = df_kospi['Close'].iloc[0]

start_date_kosdaq = df_kosdaq.index[0].date()
start_price_kosdaq = df_kosdaq['Close'].iloc[0]

start_date_usdkrw = df_usdkrw.index[0].date()
start_price_usdkrw = df_usdkrw['Close'].iloc[0]

start_date_dow = df_dow.index[0].date()
start_price_dow = df_dow['Close'].iloc[0]

start_date_nasdaq = df_nasdaq.index[0].date()
start_price_nasdaq = df_nasdaq['Close'].iloc[0]

print(f"[KOSPI] 시작 일: {start_date_kospi}, 시작 종가: {start_price_kospi:.2f}")
print(f"[KOSDAQ] 시작 일: {start_date_kosdaq}, 시작 종가: {start_price_kosdaq:.2f}")
print(f"[USD/KRW] 시작 일: {start_date_usdkrw}, 시작 환율: {start_price_usdkrw:.2f}")
print(f"[DOW JONES] 시작 일: {start_date_dow}, 시작 종가: {start_price_dow:.2f}")
print(f"[NASDAQ] 시작 일: {start_date_nasdaq}, 시작 종가: {start_price_nasdaq:.2f}")

# 그래프 출력
plt.figure(figsize=(14, 20))

# 각각 그래프
plt.subplot(7, 1, 1)
plt.plot(df_kospi.index, df_kospi['Close'], label='KOSPI', color='blue')
plt.title('KOSPI index', fontsize=13)
plt.ylabel('Clsoing price')
plt.grid(True)

plt.subplot(7, 1, 2)
plt.plot(df_kosdaq.index, df_kosdaq['Close'], label='KOSDAQ', color='orange')
plt.title('KOSDAQ index', fontsize=13)
plt.ylabel('Closing price')
plt.grid(True)

plt.subplot(7, 1, 3)
plt.plot(df_usdkrw.index, df_usdkrw['Close'], label='USD/KRW exchange rate', color='green')
plt.title('USD/KRW exchange rate', fontsize=13)
plt.ylabel('Exchange rate')
plt.grid(True)

plt.subplot(7, 1, 4)
plt.plot(df_dow.index, df_dow['Close'], label='Dow Jones', color='purple')
plt.title('Dow Jones index', fontsize=13)
plt.ylabel('Closing price')
plt.grid(True)
plt.legend()

plt.subplot(7, 1, 5)
plt.plot(df_nasdaq.index, df_nasdaq['Close'], label='NASDAQ', color='brown')
plt.title('NASDAQ index', fontsize=13)
plt.ylabel('Closing price')
plt.grid(True)
plt.legend()


# 전체 그래프
plt.subplot(7, 1, 6)  # (행, 열, 순번)
plt.plot(df_kospi.index, df_kospi['Close'], label='KOSPI', color='blue')
plt.plot(df_kosdaq.index, df_kosdaq['Close'], label='KOSDAQ', color='orange')
plt.plot(df_usdkrw.index, df_usdkrw['Close'], label='USD/KRW', color='green')
plt.plot(df_dow.index, df_dow['Close'], label='Dow Jones', color='purple')
plt.plot(df_nasdaq.index, df_nasdaq['Close'], label='NASDAQ', color='brown')
plt.title('Various index (2008~2018)', fontsize=13)
plt.ylabel('The closing price of an index')
plt.grid(True)
plt.legend()

# 정규화된 퍼센트 변화 그래프
plt.subplot(7, 1, 7)
plt.plot(kospi_norm.index, kospi_norm, label='KOSPI (Normalized)', color='blue')
plt.plot(kosdaq_norm.index, kosdaq_norm, label='KOSDAQ (Normalized)', color='orange')
plt.plot(usdkrw_norm.index, usdkrw_norm, label='USD/KRW (Norm)', color='green')
plt.plot(dow_norm.index, dow_norm, label='Dow (Normalized)', color='purple')
plt.plot(nasdaq_norm.index, nasdaq_norm, label='NASDAQ (Normalized)', color='brown')
plt.title('A percentage change (As of the Start date 100)', fontsize=14)
plt.xlabel('Date')
plt.ylabel('A percentage change (%)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()