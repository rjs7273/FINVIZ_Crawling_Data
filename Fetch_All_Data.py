import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
import time
import random
import re

class TickerDataCollector:
    def __init__(self, tickers_file='tickers.csv',results_file='financial_results.csv'):
        """클래스 초기화
        tickers_file : 티커 목록이 저장된 파일
        results_file : 수집된 데이터를 저장할 파일
        """
        self.tickers_file = tickers_file # 티커 목록 파일 이름
        self.results_file = results_file # 결과 파일 이름
        self.tickers_df = pd.DataFrame() # 로드한 티커를 저장할 데이터프레임
        self.results_df = pd.DataFrame() # 수집된 결과를 저장할 데이터프레임

        # 초기 데이터 로드
        self.load_tickers()
        self.load_results()

    def load_tickers(self):
        """티커 목록을 로드하는 메서드"""
        if os.path.exists(self.tickers_file):
            self.tickers_df = pd.read_csv(self.tickers_file)
        else:
            print(f"티커 목록 파일 '{self.tickers_file}'을 찾을 수 없습니다. Fetch_Stock_Code을 실행시켜 주세요.")
            sys.exit()

    def load_results(self):
        """재무재표 정보를 로드 or 생성하는 메서드"""
        if os.path.exists(self.results_file):
            self.results_df = pd.read_csv(self.results_file,index_col=0)
        else:
            print(f"결과 파일 '{self.results_file}'을 찾을 수 없습니다. 새 데이터프레임을 생성합니다.")
            self.results_df = self.tickers_df.copy(deep=True) # 티커명을 가지고 있는 데이터프레임 생성
            self.results_df.set_index('Tickers', inplace=True) # 티커명을 인덱스로 설정
            new_columns = [
                'Index', 'Market Cap', 'Income', 'Sales', 'Book/sh', 'Cash/sh', 'Dividend Est.',
                'Dividend TTM', 'Dividend Ex-Date', 'Employees', 'Option/Short', 'Sales Surprise',
                'SMA20', 'P/E', 'Forward P/E', 'PEG', 'P/S', 'P/B', 'P/C', 'P/FCF',
                'Quick Ratio', 'Current Ratio', 'Debt/Eq', 'LT Debt/Eq', 'EPS Surprise', 'SMA50',
                'EPS (ttm)', 'EPS next Y', 'EPS next Q', 'EPS this Y', 'EPS Growth next Y', 'EPS next 5Y',
                'EPS past 5Y', 'Sales past 5Y', 'EPS Y/Y TTM', 'Sales Y/Y TTM', 'EPS Q/Q', 'Sales Q/Q',
                'SMA200', 'Insider Own', 'Insider Trans', 'Inst Own', 'Inst Trans', 'ROA', 'ROE',
                'ROI', 'Gross Margin', 'Oper. Margin', 'Profit Margin', 'Payout', 'Earnings', 'Trades',
                'Shs Outstand', 'Shs Float', 'Short Float', 'Short Ratio', 'Short Interest', '52W Range',
                '52W High', '52W Low', 'RSI (14)', 'Recom', 'Rel Volume', 'Avg Volume', 'Volume',
                'Perf Week', 'Perf Month', 'Perf Quarter', 'Perf Half Y', 'Perf Year', 'Perf YTD',
                'Beta', 'ATR (14)', 'Volatility', 'Target Price', 'Prev Close', 'Price', 'Change'
            ]
            for col in new_columns:
                self.results_df[col] = pd.NA # 데이터프레임에 new_columns의 컬럼 열 추가

    def request_parse_data(self,ticker):
        """
        웹 페이지를 요청하고, 그 html 문서를 파싱하는 메서드
        [Parameter]
        ticker : 탐색할 티커 (string)

        [Return]
        BeautifulSoup() : BeautifulSoup 객체. 파싱된 값.
        """

        
        url = f'https://finviz.com/quote.ashx?t={ticker}&p=d'  # 요청할 url
        headers = { # 신뢰성 있는 요청을 위한 헤더 설정
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Referer': 'https://example.com',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive'
        } 

        response = requests.get(url, headers=headers) # 웹 페이지 요청
        
        """
        아래의 오류 처리 코드가 이 오류를 포괄해서 다룰 수 있으므로 주석 처리
        while response.status_code == 429: # 너무 많은 요청으로 차단된 경우
            print("너무 많은 요청.. 재시도 중")
            time.sleep(random.uniform(3, 5))
            response = requests.get(url, headers=headers)
        """
        if response.status_code != 200:
            print(f"오류 발생: 상태 코드 {response.status_code}")
            sys.exit()  # 프로그램 종료

        return BeautifulSoup(response.text, "html.parser")

    def fetch_data(self, soup): 
        """
        html 파싱 객체를 받아 재무재표 정보가 담긴 리스트를 리턴
        [Parameter]
        soup : html 파싱 객체

        [Return]
        value_list : 재무재표 정보가 담긴 리스트
        """
        table_data = [] # 테이블 내부에 있는 값들을 모두 추출한 리스트
        value_list = [] # 테이블 중 기업의 재무재표 정보만을 추출한 리스트

        table = soup.find("table", {"class" : "snapshot-table2"})
        rows = table.find_all("tr")
        
        # table_data에 table의 모든 값들을 저장
        for row in rows:
            cells = row.find_all("td")  # 각 행의 모든 셀 가져오기
            row_data = [cell.get_text(strip=True) for cell in cells]  # 텍스트 추출 및 공백 제거
            table_data.append(row_data)  # 추출한 데이터 리스트에 추가
        table_df = pd.DataFrame(table_data)

        # 필요한 데이터만 추출해 value_list에 저장
        for i in range(0,12,2): 
            value_list.extend(table_df[i + 1].tolist()) 

        return value_list

    def fetch_all_data(self):
        """
        모든 티커에 대해 데이터를 수집하는 메서드
        클래스 내에서 main 함수의 역할을 수행한다.
        """
        start_index = self.results_df['Market Cap'].count() # 탐색을 시작할 인덱스(지금까지 탐색한 인덱스 수)
        print(f"start_index : {start_index}")

        for ticker in self.results_df.index[start_index:]:
            print(f"현재 탐색 티커: {ticker}")
            soup = self.request_parse_data(ticker) # 웹 페이지 리퀘스트 & 파싱
            value_list = self.fetch_data(soup) # 파싱한 객체에서 재무재표 정보 추출
            self.results_df.loc[ticker] = value_list  # 새로운 재무재표 정보를 최종 데이터프레임에 추가

            if self.results_df['Market Cap'].count() % 10 == 0: # 10회마다 결과 저장
                self.save_results()  
        self.save_results()

    def save_results(self):
        """수집된 데이터를 CSV 파일로 저장하는 메서드."""
        print(f"결과를 저장하는 중.. 현재 {self.results_df['Market Cap'].count()}개의 재무 정보가 수집되었습니다.")
        self.results_df.to_csv(self.results_file, index=True)

if __name__ == "__main__":
    tickers_file = 'tickers.csv' # 티커 파일 경로
    financial_results_file = 'financial_results.csv' # 결과 파일 경로

    collector = TickerDataCollector(tickers_file, financial_results_file) # 객체 생성
    collector.fetch_all_data() # 데이터 수집 시작
