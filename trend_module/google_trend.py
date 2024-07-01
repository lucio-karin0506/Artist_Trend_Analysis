from pytrends.request import TrendReq

import pandas as pd

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
        
        self.pytrends = TrendReq(hl=hl, tz=tz)
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

    kw_list = ["BTS Map of the Soul: 7"]

    payload_dic = {
        'cat' : 0,
        'timeframe' : '2020-01-01 2020-08-31', # 최대 8개월까지 일별로 가져옴, 그 이상의 기간은 주별 데이터 제공
        'geo' : '',
        'gprop' : ''
    }

    google_trend = GoogleTrend(hl, tz, kw_list, payload_dic)

    # 1. 키워드 트렌드 데이터
    keyword_trend_df = google_trend.get_keyword_trend()
    print(keyword_trend_df)