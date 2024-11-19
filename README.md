# FINVIZ Stock Data Collector

이 프로젝트는 FINVIZ 웹사이트에서 주식 관련 데이터를 수집하고 분석하는 도구입니다. 두 가지 주요 코드 파일을 포함하며, 각각 티커(종목 코드) 수집과 주식 데이터를 수집하는 역할을 수행합니다.  
README는 ChatGPT로 대충 작성했습니다..

## 주요 기능
1. **티커 수집**: `Fetch_Stock_Code.py`를 통해 FINVIZ 웹사이트에서 모든 주식 티커를 수집하여 CSV 파일로 저장합니다.
2. **데이터 수집**: `Fetch_All_Data.py`를 통해 각 주식 티커에 대한 금융 데이터를 수집하고 CSV 파일에 저장합니다.

---

## 코드 설명

### `Fetch_Stock_Code.py`
- **설명**: FINVIZ 웹사이트에서 모든 주식 티커를 수집하는 스크립트입니다.
- **기능**:
  - **load_tickers()**: 기존에 저장된 티커를 로드합니다.
  - **fetch_all_tickers()**: 모든 티커를 순차적으로 수집하며 중복을 제거합니다.
  - **fetch_single_ticker()**: 웹 페이지에서 한 번에 티커 목록을 파싱합니다.
  - **save_tickers()**: 수집한 티커 목록을 `tickers.csv`로 저장합니다.
- **사용법**:
  ```bash
  python Fetch_Stock_Code.py
