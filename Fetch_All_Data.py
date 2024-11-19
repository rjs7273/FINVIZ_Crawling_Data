import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import sys
import re

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
            # self.tickers_df = self.tickers_df.sort_values(by='Tickers') # 인덱스가 무작위적으로 섞여 있어서 정렬
            # self.tickers = df['Tickers']
            # print(f"로드한 티커 : {self.tickers_df['Tickers'][:5]}")
        else:
            print(f"티커 목록 파일 '{self.tickers_file}'을 찾을 수 없습니다. Fetch_Stock_Code을 실행시켜 주세요.")
            sys.exit()

    def load_results(self):
        """이전에 저장된 결과 파일을 로드하는 메서드"""
        if os.path.exists(self.results_file):
            self.results_df = pd.read_csv(self.results_file,index_col=0)
            # self.results_df = self.tickers_df.copy(deep=True) # 결과 데이터프레임에 티커 추가
            # self.results_df.set_index('Tickers', inplace=True) # 티커명을 인덱스로 설정
            # self.save_results()
        else:
            print(f"결과 파일 '{self.results_file}'을 찾을 수 없습니다.")
            self.results_df = self.tickers_df.copy(deep=True) # 결과 데이터프레임에 티커 추가
            self.results_df.set_index('Tickers', inplace=True) # 티커명을 인덱스로 설정
            # print(f"self.results_df.index : {self.results_df.index}")
            # self.results_df.to_csv('test1.csv', index=True)
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
                self.results_df[col] = pd.NA
            # self.results_df.to_csv("test.csv", index=True)
            # print(f"self.results_df.shape : {self.results_df.shape}")
            # print(f"self.results_df.columns : {self.results_df.columns}")
            # print(f"len(self.results_df) : {self.results_df}")
            # print(f"self.results_df.colums : {self.results_df.columns}")

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
        response_data = response.text
        if response.status_code != 200:
            print(f"오류 발생: 상태 코드 {response.status_code}")
            sys.exit()  # 프로그램 종료
        # print(f"response_status_code : {response.status_code}")
        # print(f"response : {response_data}")
        # with open("output.txt", "w", encoding="utf-8") as file:
        #     file.write(response_data)
        return BeautifulSoup(response.text, "html.parser")

    def parse_table(self, soup):
        # print(f"soup : {soup.get_text()}") # soup는 제대로 출력됨
        # soup_data = soup.get_text()
        # print(f"type(soup_data) : {type(soup_data)}")
        # with open("output.txt", "w", encoding="utf-8") as file:
        #     file.write(soup_data)
        table = soup.find("table", {"class" : "snapshot-table2"})
        # print(f"table : {table}") # 빈 테이블이 나옴
        rows = table.find_all("tr")
        table_data = []

        # print(f"rows : {rows}")

        for row in rows:
            cells = row.find_all("td")  # 각 행의 모든 셀 가져오기
            row_data = [cell.get_text(strip=True) for cell in cells]  # 텍스트 추출 및 공백 제거
            table_data.append(row_data)  # 추출한 데이터 리스트에 추가

        # 데이터프레임으로 변환
        df = pd.DataFrame(table_data)
        value_list = []
        index_list = []
        for i in range(0,12,2): # 필요한 데이터만 추출
            # index_list.extend(df[i].tolist())
            value_list.extend(df[i + 1].tolist()) # 짝수 열의 데이터만 추가
        # print(f"index_list : {index_list}")
        # print(f"value_list : {value_list}")
        return value_list

    # 모든 티커에 대해 데이터를 수집하는 메서드
    def collect_data(self):
        start_index = self.results_df['Market Cap'].count() # 이미 수집된 데이터 개수
        print(f"start_index : {start_index}")
        # start_ticker = self.results_df.index.get_loc(start_index)

        for ticker in self.results_df.index[start_index:]:
            print(f"현재 탐색 티커: {ticker}")
            soup = self.fetch_data(ticker)  # 웹 페이지 데이터 가져오기
            # print(f"soup : {soup}")
            value_list = self.parse_table(soup)  # 테이블 데이터 파싱
            # print(f"value_list : {value_list}")
            # print(f"len(value_list) : {len(value_list)}")
            # print(f"len(self.results_df.loc[ticker]) : {len(self.results_df.loc[ticker])}")
            self.results_df.loc[ticker] = value_list  # 데이터프레임에 추가
            if self.results_df['Market Cap'].count() % 10 == 0:
                self.save_results()  # 결과 저장
        self.save_results()

    def save_results(self):
        """수집된 데이터를 CSV 파일로 저장하는 메서드.
        메모리 과부화를 막기 위해 10개의 티커마다 저장하도록 기능하면 좋겠다."""
        print(f"결과를 저장하는 중 : {self.results_file}")
        self.results_df.to_csv(self.results_file, index=True)

if __name__ == "__main__":
    tickers_file = 'tickers.csv' # 티커 파일 경로
    financial_results_file = 'financial_results.csv' # 결과 파일 경로

    collector = TickerDataCollector(tickers_file, financial_results_file) # 객체 생성
    collector.collect_data() # 데이터 수집 시작
