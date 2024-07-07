from bs4 import BeautifulSoup
from selenium import webdriver

import pandas as pd

def get_album_chart(year: int):

    url = f"https://circlechart.kr/page_chart/album.circle?nationGbn=T&targetTime={year}&hitYear={year}&termGbn=year&yearTime=3"

    # Selenium WebDriver 설정
    driver = webdriver.Chrome()
    driver.get(url)

    # 페이지 로드 시간 지정 (필요에 따라 조정)
    driver.implicitly_wait(10)

    # 페이지 소스 로드
    page_source = driver.page_source

    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(page_source, 'html.parser')

    # 테이블 데이터 로드
    table = soup.find('tbody', {'id': 'pc_chart_tbody'})

    albums = []; artists = []; sales_list = []; distributions = []
    for row in table.select('tr'):

        td_info = row.find_all('td')

        album = td_info[2].select_one('div > section:nth-child(2) > div > div.font-bold.mb-2').text
        artist = td_info[2].select_one('div > section:nth-child(2) > div > div.text-sm.text-gray-400.font-bold').text
        sales = td_info[3].select_one('span').text
        distribution = td_info[4].select_one('div > span').text

        albums.append(album)
        artists.append(artist)
        sales_list.append(sales)
        distributions.append(distribution)
        
    album_chart_df = pd.DataFrame(data={'album' : albums, 'artist' : artists, 'sales' : sales_list, 'distribution' : distributions})

    return album_chart_df


if __name__ == '__main__':

    album_chart_df_list = []
    for year in [2020, 2021, 2022, 2023]:

        album_chart_df = get_album_chart(year=year)
        album_chart_df['year'] = year
        album_chart_df_list.append(album_chart_df)

    final_album_chart_df = pd.concat(album_chart_df_list, ignore_index=True)

    print(final_album_chart_df)
    # final_album_chart_df.to_csv('album_chart_info.csv', encoding='utf-8-sig')