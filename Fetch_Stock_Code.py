import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import time
import random


class TickerCrawler:
    def __init__(self, csv_file='tickers.csv'):
        self.csv_file = csv_file
        self.tickers = set()
        self.past_tickers = set()
        self.ticker_num = 0
        self.load_tickers()

    def load_tickers(self):
        if os.path.exists(self.csv_file):
            tickers_df = pd.read_csv(self.csv_file)
            self.tickers = set(tickers_df['Tickers'].tolist())
            self.ticker_num = len(self.tickers) // 20
            print(f"이전에 {len(self.tickers)}개의 티커가 로드되었습니다.")
        else:
            print("이전에 저장된 티커가 없습니다.")
        
    def fetch_all_tickers(self):
        while True:
            new_tickers = self.fetch_single_ticker()
            if new_tickers == 'Error':
                continue
            elif new_tickers == self.past_tickers:
                self.save_tickers()
                print("마지막 페이지에 도달")
                break
            else:
                self.past_tickers = new_tickers.copy()
                self.tickers.update(new_tickers)
                # print(self.tickers)
                self.ticker_num += 1
            
            if self.ticker_num % 10 == 0:
                self.save_tickers()
        
                
    def fetch_single_ticker(self):
        """웹페이지 로드를 요청"""
        url = f"https://finviz.com/screener.ashx?v=111&f=ind_stocksonly&r={1 + self.ticker_num * 20}"
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

        if res.status_code != 200:
            print(f"요청 실패... 현재 status_code는 {res.status_code}입니다.")
            time.sleep(random.uniform(3,5))
            return 'Error'
        
        """html 파일에서 티커명을 파싱하기"""
        soup = BeautifulSoup(res.text, 'html.parser')
        cells = soup.find_all('td', {
            'data-boxover': re.compile(r'cssbody=\[hoverchart\]'),
            'align': 'left'
        })
        new_tickers = set()
        for cell in cells:
            a_tag = cell.find('a')
            if a_tag:
                ticker = a_tag.get_text()
                new_tickers.add(ticker)
        # print(f"new_tickers : {new_tickers}") 
        return new_tickers
    def save_tickers(self):
        tickers_list = list(self.tickers)
        tickers_list = [str(item) for item in tickers_list]
        tickers_list.sort()
        tickers_df = pd.DataFrame(tickers_list, columns=['Tickers'])
        print(f"진행 결과 저장.. 총 {len(tickers_list)}개의 티커를 로드했습니다.")
        tickers_df.to_csv("tickers.csv",index=False)
        
    
ticker_crawler = TickerCrawler()

ticker_crawler.fetch_all_tickers()