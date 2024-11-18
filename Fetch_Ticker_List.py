import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import time
import random

# 티커명 저장을 위한 세트
tickers = set()

# 티커 목록을 저장할 파일 경로
tickers_file = 'tickers.csv'

# 이전에 저장된 티커 로드 (CSV 파일이 존재하는 경우)
if os.path.exists(tickers_file):
    tickers_df = pd.read_csv(tickers_file)
    tickers.update(tickers_df['Tickers'].tolist())

ticker_num = len(tickers) // 20  # 저장된 티커 수에 맞게 시작 페이지 조정

print("실행됨")

while True:
    new_tickers = set()
    # 요청을 보내고 HTML 페이지 가져오기
    url = f"https://finviz.com/screener.ashx?v=111&f=ind_stocksonly&r={1 + ticker_num * 20}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://finviz.com/',
        'TE': 'Trailers',
        'Cache-Control': 'max-age=0'
    }
    res = requests.get(url, headers=headers)

    if res.status_code == 429:
        print("너무 많은 요청.. 재시도")
        time.sleep(random.uniform(3, 5))
        continue

    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(res.text, 'html.parser')

    # 티커명이 들어있는 HTML 요소 찾기
    cells = soup.find_all('td', {
        'data-boxover': re.compile(r'cssbody=\[hoverchart\]'),
        'align': 'left'
    })

    # 각 티커명 추출
    for cell in cells:
        a_tag = cell.find('a')
        if a_tag:
            ticker = a_tag.get_text()
            new_tickers.add(ticker)

    # 종료 조건 설정
    if not new_tickers:
        break
    else:
        tickers.update(new_tickers)
        ticker_num += 1

    # 진행 상황을 CSV 파일에 저장
    tickers_df = pd.DataFrame(list(tickers), columns=['Tickers'])
    tickers_df.to_csv(tickers_file, index=False)

    print(f"현재까지 {len(tickers)}개의 티커를 추출했습니다.")
    print(f"ticker_num은 {ticker_num}입니다.")
