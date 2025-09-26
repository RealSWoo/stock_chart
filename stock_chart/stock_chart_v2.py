import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# ================== 설정 ==================
start_date = '2008-01-01'
end_date   = '2018-12-31'

# Windows 경로 → raw string 권장 (혹은 'D:\\VSCODE\\stock_chart\\...')
EVENTS_CSV = r'D:\VSCODE\stock_chart\market_events_2008_2018_us_china.csv'
KEEP_COUNTRIES = {'United States', 'China'}
INCLUDE_CATEGORIES = {'banking', 'systemic', 'currency', 'inflation', 'sovereign_default'}

SHOW_LABELS = False   # True로 하면 각 선에 간단 라벨 표시(혼잡할 수 있음)

# ================== 지수 데이터 ==================
df_kospi  = fdr.DataReader('KS11', start_date, end_date)
df_kosdaq = fdr.DataReader('KQ11', start_date, end_date)
df_usdkrw = fdr.DataReader('USD/KRW', start_date, end_date)
df_dow    = fdr.DataReader('DJI', start_date, end_date)
df_nasdaq = fdr.DataReader('IXIC', start_date, end_date)

print(f"[KOSPI] : {df_kospi.columns}")
print(f"[KOSDAQ] : {df_kosdaq.columns}")
print(f"[USD/KRW] : {df_usdkrw.columns}")
print(f"[DOW JONES] : {df_dow.columns}")
print(f"[NASDAQ] : {df_nasdaq.columns}")

# 정규화: 시작일 대비 100
kospi_norm  = df_kospi['Close']  / df_kospi['Close'].iloc[0]  * 100
kosdaq_norm = df_kosdaq['Close'] / df_kosdaq['Close'].iloc[0] * 100
usdkrw_norm = df_usdkrw['Close'] / df_usdkrw['Close'].iloc[0] * 100
dow_norm    = df_dow['Close']    / df_dow['Close'].iloc[0]    * 100
nasdaq_norm = df_nasdaq['Close'] / df_nasdaq['Close'].iloc[0] * 100

# ================== 이벤트 로딩 & 전처리 ==================
ev = pd.read_csv(EVENTS_CSV)

# 필수 컬럼 체크 및 파싱
if 'start_date' not in ev.columns:
    raise ValueError(f"'start_date' 컬럼이 없습니다. 컬럼들: {list(ev.columns)}")
if 'end_date' not in ev.columns:
    # Harvard 변환본엔 end_date가 있으므로 보통 필요 없음. 없을 경우 start_date로 채움
    ev['end_date'] = ev['start_date']

ev['start_date'] = pd.to_datetime(ev['start_date'], errors='coerce')
ev['end_date']   = pd.to_datetime(ev['end_date'], errors='coerce')
ev['country']    = ev['country'].astype(str).str.strip()

# 국가/카테고리/기간 필터
ev = ev[
    ev['country'].isin(KEEP_COUNTRIES) &
    ev['category'].isin(INCLUDE_CATEGORIES)
].copy()

start_dt = pd.to_datetime(start_date)
end_dt   = pd.to_datetime(end_date)
# 이벤트 구간이 차트 구간과 겹치는 것만 유지 (기간형 이벤트 고려)
ev = ev[(ev['start_date'] <= end_dt) & (ev['end_date'] >= start_dt)].copy()

# ===== 핵심: 연중 중간일(mid-date) 계산 → 날짜당 1개 라인 =====
# (기간형: 중간일, 단일일: 그 날짜 그대로)
ev['mid_date'] = ev['start_date'] + (ev['end_date'] - ev['start_date'])/2
ev['mid_date'] = ev['mid_date'].fillna(ev['start_date'])
ev_dates = (
    ev['mid_date']
    .dropna()
    .dt.normalize()
    .drop_duplicates()
    .sort_values()
    .to_list()
)

print(f"[DEBUG] 이벤트 mid-date 개수: {len(ev_dates)}")
if len(ev_dates) > 0:
    print(f"[DEBUG] 첫 10개 mid-date: {ev_dates[:10]}")
else:
    print("[DEBUG] ev_dates가 비어있습니다. CSV/필터를 확인하세요.")

ev_labels = (
    ev.groupby(ev['mid_date'].dt.normalize())
      .apply(lambda g: "; ".join(
          f"{r['country']}:{r['category']}" for _, r in g.iterrows()
      ))
      .to_dict()
)
ev_dates = list(ev_labels.keys())

print("[DEBUG] 이벤트 날짜/라벨 샘플:")
for d in list(ev_labels.keys())[:5]:
    print(d, "=>", ev_labels[d])

# (선택) 국가별로 따로 쓰고 싶다면:
ev_dates_us = (ev[ev['country'].eq('United States')]['mid_date'].dt.normalize()
               .dropna().drop_duplicates().sort_values().to_list())
ev_dates_cn = (ev[ev['country'].eq('China')]['mid_date'].dt.normalize()
               .dropna().drop_duplicates().sort_values().to_list())

# ================== 이벤트 선 그리기 함수 ==================
def add_event_date_lines(ax, dates, label_prefix=None, show_labels=False):
    for d in dates:
        ax.axvline(d, linestyle='--', alpha=0.6, linewidth=1.0)
        if show_labels:
            txt = (label_prefix or 'E')
            ax.text(d, ax.get_ylim()[1], txt, rotation=90,
                    va='bottom', ha='center', fontsize=7, alpha=0.6)

# ================== 그래프 ==================
plt.figure(figsize=(14, 20))

# 1) KOSPI (중국/미국 합집합 혹은 중국만 사용하려면 ev_dates_cn으로 교체)
ax1 = plt.subplot(7, 1, 1)
ax1.plot(df_kospi.index, df_kospi['Close'], label='KOSPI')
ax1.set_title('KOSPI index', fontsize=13); ax1.set_ylabel('Closing price'); ax1.grid(True)
add_event_date_lines(ax1, ev_dates, ev_labels, show_labels=False)   # ev_dates_cn로 바꾸면 중국 사건만

# 2) KOSDAQ
ax2 = plt.subplot(7, 1, 2)
ax2.plot(df_kosdaq.index, df_kosdaq['Close'], label='KOSDAQ')
ax2.set_title('KOSDAQ index', fontsize=13); ax2.set_ylabel('Closing price'); ax2.grid(True)
add_event_date_lines(ax2, ev_dates, ev_labels, show_labels=False)

# 3) USD/KRW
ax3 = plt.subplot(7, 1, 3)
ax3.plot(df_usdkrw.index, df_usdkrw['Close'], label='USD/KRW')
ax3.set_title('USD/KRW exchange rate', fontsize=13); ax3.set_ylabel('Exchange rate'); ax3.grid(True)
add_event_date_lines(ax3, ev_dates, ev_labels, show_labels=False)

# 4) DOW JONES (미국만 쓰고 싶으면 ev_dates_us)
ax4 = plt.subplot(7, 1, 4)
ax4.plot(df_dow.index, df_dow['Close'], label='Dow Jones')
ax4.set_title('Dow Jones index', fontsize=13); ax4.set_ylabel('Closing price'); ax4.grid(True)
add_event_date_lines(ax4, ev_dates, ev_labels, show_labels=False)
ax4.legend()

# 5) NASDAQ (미국만 쓰고 싶으면 ev_dates_us)
ax5 = plt.subplot(7, 1, 5)
ax5.plot(df_nasdaq.index, df_nasdaq['Close'], label='NASDAQ')
ax5.set_title('NASDAQ index', fontsize=13); ax5.set_ylabel('Closing price'); ax5.grid(True)
add_event_date_lines(ax5, ev_dates, ev_labels, show_labels=False)
ax5.legend()

# 6) 전체(종가)
ax6 = plt.subplot(7, 1, 6)
ax6.plot(df_kospi.index, df_kospi['Close'], label='KOSPI')
ax6.plot(df_kosdaq.index, df_kosdaq['Close'], label='KOSDAQ')
ax6.plot(df_usdkrw.index, df_usdkrw['Close'], label='USD/KRW')
ax6.plot(df_dow.index, df_dow['Close'], label='Dow Jones')
ax6.plot(df_nasdaq.index, df_nasdaq['Close'], label='NASDAQ')
ax6.set_title('Various index (2008~2018)', fontsize=13)
ax6.set_ylabel('The closing price of an index'); ax6.grid(True); ax6.legend()
add_event_date_lines(ax6, ev_dates, ev_labels, show_labels=False)

# 7) 정규화
ax7 = plt.subplot(7, 1, 7)
ax7.plot(kospi_norm.index, kospi_norm, label='KOSPI (Normalized)')
ax7.plot(kosdaq_norm.index, kosdaq_norm, label='KOSDAQ (Normalized)')
ax7.plot(usdkrw_norm.index, usdkrw_norm, label='USD/KRW (Norm)')
ax7.plot(dow_norm.index,    dow_norm,    label='Dow (Normalized)')
ax7.plot(nasdaq_norm.index, nasdaq_norm, label='NASDAQ (Normalized)')
ax7.set_title('A percentage change (As of the Start date 100)', fontsize=14)
ax7.set_xlabel('Date'); ax7.set_ylabel('A percentage change (%)'); ax7.grid(True); ax7.legend()
add_event_date_lines(ax7, ev_dates, ev_labels, show_labels=False)

plt.tight_layout()
plt.show()

# ================== 시작일 정보 출력(기존 코드 유지) ==================
start_date_kospi  = df_kospi.index[0].date();  start_price_kospi  = df_kospi['Close'].iloc[0]
start_date_kosdaq = df_kosdaq.index[0].date(); start_price_kosdaq = df_kosdaq['Close'].iloc[0]
start_date_usdkrw = df_usdkrw.index[0].date(); start_price_usdkrw = df_usdkrw['Close'].iloc[0]
start_date_dow    = df_dow.index[0].date();    start_price_dow    = df_dow['Close'].iloc[0]
start_date_nasdaq = df_nasdaq.index[0].date(); start_price_nasdaq = df_nasdaq['Close'].iloc[0]

print(f"[KOSPI] 시작 일: {start_date_kospi}, 시작 종가: {start_price_kospi:.2f}")
print(f"[KOSDAQ] 시작 일: {start_date_kosdaq}, 시작 종가: {start_price_kosdaq:.2f}")
print(f"[USD/KRW] 시작 일: {start_date_usdkrw}, 시작 환율: {start_price_usdkrw:.2f}")
print(f"[DOW JONES] 시작 일: {start_date_dow}, 시작 종가: {start_price_dow:.2f}")
print(f"[NASDAQ] 시작 일: {start_date_nasdaq}, 시작 종가: {start_price_nasdaq:.2f}")