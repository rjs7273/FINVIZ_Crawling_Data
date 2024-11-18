import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import sys

class TickerDataCollector:
    def __init__(self, tickers_file='tickers.csv',results_file='financial_results.csv'):
        """클래스 초기화
        tickers_file : 티커 목록이 저장된 파일
        results_file : 수집된 데이터를 저장할 파일
        """
        self.tickers_file = tickers_file # 티커 목록 파일 경로
        self.results_file = results_file # 결과 파일 경로
        self.tickers_df = pd.DataFrame() # 로드한 티커를 저장할 데이터프레임
        self.results_df = pd.DataFrame() # 수집된 결과를 저장할 데이터프레임

        # 초기 데이터 로드
        self.load_tickers()
        self.load_results()

    def load_tickers(self):
        """티커 목록을 로드하는 메서드"""
        if os.path.exists(self.tickers_file):
            self.tickers_df = pd.read_csv(self.tickers_file)
            self.tickers_df = self.tickers_df.sort_values(by='Tickers') # 인덱스가 무작위적으로 섞여 있어서 정렬
            # self.tickers = df['Tickers']
            print(f"로드한 티커 : {self.tickers_df['Tickers'][:5]}")
        else:
            print(f"티커 목록 파일 '{self.tickers_file}'을 찾을 수 없습니다. Fetch_Stock_Code을 실행시켜 주세요.")
            sys.exit()

    def load_results(self):
        """이전에 저장된 결과 파일을 로드하는 메서드"""
        if os.path.exists(self.results_file):
            self.results_df = pd.read_csv(self.results_file)
        else:
            print(f"결과 파일 '{self.results_file}'을 찾을 수 없습니다.")
            self.results_df = self.results_df.copy(deep=True) # 결과 데이터프레임에 티커 추가,
            self.results_df.set_index('Tickers', inplace=True) # 티커명을 인덱스로 설정
            self.results_df.columns = [
                'Index', 'Market Cap', 'Income', 'Sales', 'Book/sh', 'Cash/sh', 
                'Dividend Est.', 'Dividend TTM', 'Dividend Ex-Date', 'Employees', 
                'Option/Short', 'Sales Surprise', 'SMA20', 'P/E', 'Forward P/E', 
                'PEG', 'P/S', 'P/B', 'P/C', 'P/FCF', 'Quick Ratio', 'Current Ratio', 
                'Debt/Eq', 'LT Debt/Eq', 'EPS Surprise', 'SMA50', 'EPS (ttm)', 
                'EPS next Y', 'EPS next Q', 'EPS this Y', 'EPS next 5Y', 'EPS past 5Y', 
                'Sales past 5Y', 'EPS Y/Y TTM', 'Sales Y/Y TTM', 'EPS Q/Q', 'Sales Q/Q', 
                'SMA200', 'Insider Own', 'Insider Trans', 'Inst Own', 'Inst Trans', 
                'ROA', 'ROE', 'ROI', 'Gross Margin', 'Oper. Margin', 'Profit Margin', 
                'Payout', 'Earnings', 'Trades', 'Shs Outstand', 'Shs Float', 
                'Short Float', 'Short Ratio', 'Short Interest', '52W Range', 
                '52W High', '52W Low', 'RSI (14)', 'Recom', 'Rel Volume', 
                'Avg Volume', 'Volume', 'Perf Week', 'Perf Month', 'Perf Quarter', 
                'Perf Half Y', 'Perf Year', 'Perf YTD', 'Beta', 'ATR (14)', 
                'Volatility', 'Target Price', 'Prev Close', 'Price', 'Change'
            ] # 데이터 열을 추가.

    def fetch_data(self,ticker):
        """웹 페이지를 요청하는 메서드.
        파싱한 데이터를 리턴하지만, 파싱 기능은 parse_table에 따로 구현하도록 하자."""
        url = f'https://finviz.com/quote.ashx?t={ticker}&p=d'  # 요청할 URL 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Referer': 'https://example.com',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive'
        }

        response = requests.get(url, headers=headers) # 웹 페이지 요청
        while response.status_code == 429: # 너무 많은 요청으로 차단된 경우
            print("너무 많은 요청.. 재시도 중")
            time.sleep(random.uniform(3, 5))
            response = requests.get(url, headers=headers)
        return BeautifulSoup(response.text, "html.parser")

    def parse_table(self, html_data):
        """파싱한 html 테이블에서 특정 속성을 이용해 데이터를 추출하자. """
        # 실제 데이터 파싱 로직은 나중에 구현(BeautifulSoup 사용)
        # print(f"파싱 중 : {html_data}")
        return ["Parsed Data"] # 더미 파싱 결과 (실제 파싱 로직으로 대체)

    def collect_data(self):
        """모든 티커에 대해 데이터를 수집하는 메서드.
        for문을 이용해 기존에 탐색했던 구간부터, 문서의 끝까지 탐색해야 한다."""
        for ticker in self.results_df.index[:10]: # 임시로 10개의 티커만 탐색하도록 지정
            html_data = self.fetch_data(ticker)
            parsed_data = self.parse_table(html_data)
            self.results_df.loc[ticker] = parsed_data
            if len(self.results_df) % 10 == 0:
                self.save_results()
    def save_results(self):
        """수집된 데이터를 CSV 파일로 저장하는 메서드.
        메모리 과부화를 막기 위해 10개의 티커마다 저장하도록 기능하면 좋겠다."""
        print(f"결과를 저장하는 중 : {self.results_file}")
        self.results_df.to_csv(self.results_file, index=False)

if __name__ == "__main__":
    tickers_file = 'tickers.csv' # 티커 파일 경로
    financial_results_file = 'financial_results.csv' # 결과 파일 경로

    collector = TickerDataCollector(tickers_file, financial_results_file) # 객체 생성
    collector.collect_data() # 데이터 수집 시작
