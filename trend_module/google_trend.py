from pytrends.request import TrendReq

import pandas as pd

from datetime import datetime, timedelta

class GoogleTrend:

    def __init__(self, hl: str, tz: int, kw_list: list, payload_dic: dict) -> None:
        '''구글 trend 설정 정보 생성자 초기화

            @Args:
                -hl: Google Trends 인터페이스 언어 설정 (host language)

                -tz: 시간대 오프셋 설정 (Timezone Offset)

                -kw_list: 검색 키워드 리스트

                -payload_dic: 트렌드 검색 상세 조건 딕셔너리

            @Returns:
                -None
        '''
        
        self.pytrends = TrendReq(
                            hl=hl,
                            tz=tz,
                            timeout=(10, 25)
                        )
        
        self.pytrends.build_payload(
                            kw_list,
                            cat=payload_dic['cat'],
                            timeframe=payload_dic['timeframe'],
                            geo=payload_dic['geo'],
                            gprop=payload_dic['gprop']
                        )


    def get_keyword_trend(self) -> pd.DataFrame:
        '''시간대 별 검색 키워드 트렌드 데이터 로드

            @Args:
                -None

            @Returns:
                -keyword_trend_df: 시간대 별 검색 키워드 트렌드 데이터
        '''

        # 시간에 따른 검색 트렌드 데이터 가져오기
        keyword_trend_df = self.pytrends.interest_over_time()

        return keyword_trend_df


if __name__ == '__main__':

    hl='en-US'; tz=360

    kw_list = ["BTS"]

    timeframe = '2020-01-01 2021-01-01'
    start_date, end_date = datetime.strptime(timeframe.split(' ')[0], '%Y-%m-%d'), datetime.strptime(timeframe.split(' ')[1], '%Y-%m-%d')
    period = (end_date - start_date).days
    
    # 가져올 데이터가 6개월 이하인 경우,
    if period <= 180:
        payload_dic = {
            'cat' : 0,
            'timeframe' : timeframe, # 최대 8개월까지 일별로 가져옴, 그 이상의 기간은 주별 데이터 제공
            'geo' : '',
            'gprop' : ''
        }

        google_trend = GoogleTrend(hl, tz, kw_list, payload_dic)

        # 1. 키워드 트렌드 데이터
        keyword_trend_df = google_trend.get_keyword_trend()
        print(keyword_trend_df)
    
    # 가져올 데이터 6개월 초과인 경우,
    else:

        # 날짜 범위 6개월 미만 split
        timeframes = []
        while start_date < end_date:
            next_date = start_date + timedelta(days=180)
            if next_date > end_date:
                next_date = end_date

            timeframes.append(f'{start_date.strftime("%Y-%m-%d")} {next_date.strftime("%Y-%m-%d")}')
            start_date = next_date

        # 기간 별 데이터 요청
        keyword_trend_df_list = []
        for timeframe in timeframes:
            payload_dic = {
                'cat' : 0,
                'timeframe' : timeframe, # 최대 8개월까지 일별로 가져옴, 그 이상의 기간은 주별 데이터 제공
                'geo' : '',
                'gprop' : ''
            }

            google_trend = GoogleTrend(hl, tz, kw_list, payload_dic)

            # 1. 키워드 트렌드 데이터
            single_keyword_trend_df = google_trend.get_keyword_trend()
            keyword_trend_df_list.append(single_keyword_trend_df)

        keyword_trend_df = pd.concat(keyword_trend_df_list).drop_duplicates(keep='first')
        print(keyword_trend_df)