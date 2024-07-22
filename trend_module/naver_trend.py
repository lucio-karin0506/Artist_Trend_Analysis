import json
import urllib.request

import pandas as pd

class NaverTrend:

    def __init__(self, acc_info: dict) -> None:
        '''naver trend api 계정 생성자 초기화

            @Args:
                -acc_info: naver trend 계정 딕셔너리

            @Returns:
                -None
        '''

        client_id = acc_info['id']; client_secret = acc_info['secret']

        url = 'https://openapi.naver.com/v1/datalab/search'

        self.request = urllib.request.Request(url)
        self.request.add_header("X-Naver-Client-Id", client_id)
        self.request.add_header("X-Naver-Client-Secret", client_secret)
        self.request.add_header("Content-Type","application/json")


    def get_keyword_trend(self, body_dic: dict) -> pd.DataFrame:
        '''naver trend 검색량 get

            @Args:
                -body_dic: 검색량 request body

            @Returns:
                -keyword_trend_df: naver trend 검색량
        '''

        body_json = json.dumps(body_dic)

        keyword_trend_response = urllib.request.urlopen(self.request, data=body_json.encode('utf-8'))
        keyword_trend_response = json.loads(keyword_trend_response.read().decode('utf-8'))

        rows = []
        keyword_result_list = keyword_trend_response['results']
        for keyword_result in keyword_result_list:
            title = keyword_result['title']

            for entry in keyword_result['data']:
                period = entry['period']
                ratio = entry['ratio']
                rows.append({"period": period, "title": title, "ratio": ratio})

        keyword_trend_df = pd.DataFrame(rows).set_index('period').pivot(columns='title', values='ratio')

        return keyword_trend_df


if __name__ == '__main__':

    with open(r'account_info\naver_trend_account_info.json', 'r') as file: naver_acc_info = json.load(file)

    # 1. naver trend 계정 생성
    naver_trend = NaverTrend(naver_acc_info)

    # 2. keyword 검색량 get
    '''
        - 보이그룹: 세븐틴, 방탄소년단, Stray Kids, NCT DREAM, 투모로우바이투게더
        - 걸그룹: IVE, aespa, NewJeans, TWICE, BLACKPINK
    '''
    body = {
        'startDate' : '2019-01-01',
        'endDate' : '2024-06-30',
        'timeUnit' : 'date',
        'keywordGroups' : [
            {'groupName' : 'IVE', 'keywords' : ['IVE', 'ive', '아이브']},
            {'groupName' : 'AESPA', 'keywords' : ['AESPA', 'aespa', '에스파']},
            {'groupName' : 'NEWJEANS', 'keywords' : ['NEWJEANS', 'NewJeans', 'newjeans', '뉴진스']},
            {'groupName' : 'TWICE', 'keywords' : ['TWICE', 'twice', '트와이스']},
            {'groupName' : 'BLACKPINK', 'keywords' : ['BLACKPINK', 'blackpink', '블랙핑크', '블핑']}
        ]
    }
    keyword_trend_df = naver_trend.get_keyword_trend(body)
    print(keyword_trend_df)
    # keyword_trend_df.to_csv('girlgroup_naver_trend.csv', encoding='utf-8-sig')