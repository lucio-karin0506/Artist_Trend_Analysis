from bs4 import BeautifulSoup
from selenium import webdriver

import pandas as pd


def get_bs4_soup(url: str, page_load_time: int=10):

    # Selenium WebDriver 설정
    driver = webdriver.Chrome()
    driver.get(url)

    # 페이지 로드 시간 지정 (필요에 따라 조정)
    driver.implicitly_wait(page_load_time)

    # 페이지 소스 로드
    page_source = driver.page_source

    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(page_source, 'html.parser')

    return soup


def get_yearly_album_chart(year: str):

    url = f"https://circlechart.kr/page_chart/album.circle?nationGbn=T&targetTime={year}&hitYear={year}&termGbn=year&yearTime=3"

    soup = get_bs4_soup(url)

    # 테이블 데이터 로드
    table = soup.find('tbody', {'id': 'pc_chart_tbody'})

    albums = []; artists = []; sales_list = []; distributions = []
    for row in table.select('tr'):

        td_info = row.find_all('td')

        album = td_info[2].select_one('div > section:nth-child(2) > div > div.font-bold.mb-2').text
        artist = td_info[2].select_one('div > section:nth-child(2) > div > div.text-sm.text-gray-400.font-bold').text
        sales = int(td_info[3].select_one('span').text.replace(',', ''))
        distribution = td_info[4].select_one('div > span').text

        albums.append(album)
        artists.append(artist)
        sales_list.append(sales)
        distributions.append(distribution)
        
    album_chart_df = pd.DataFrame(data={'album' : albums, 'artist' : artists, 'sales' : sales_list, 'distribution' : distributions})
    album_chart_df['date'] = year

    return album_chart_df


def get_monthly_album_chart(date) -> pd.DataFrame:

    year = date[:4]; month = date[4:]

    url = f'https://circlechart.kr/page_chart/album.circle?nationGbn=T&targetTime={month}&hitYear={year}&termGbn=month&yearTime=3'

    soup = get_bs4_soup(url)

    # 테이블 데이터 로드
    table = soup.find('tbody', {'id': 'pc_chart_tbody'})

    albums = []; artists = []; sales_list = []; cum_sales_list = []; distributions = []
    for row in table.select('tr'):

        td_info = row.find_all('td')

        album = td_info[2].select_one('div > section:nth-child(2) > div > div.font-bold.mb-2').text
        artist = td_info[2].select_one('div > section:nth-child(2) > div > div.text-sm.text-gray-400.font-bold').text
        sales = int((td_info[3].select_one('span').text).split('/')[0].replace(',', ''))
        cum_sales = int((td_info[3].select_one('span').text).split('/')[1].replace(',', ''))
        distribution = td_info[4].select_one('div > span').text

        albums.append(album)
        artists.append(artist)
        sales_list.append(sales)
        cum_sales_list.append(cum_sales)
        distributions.append(distribution)
        
    album_chart_df = pd.DataFrame(data={'album' : albums, 'artist' : artists, 'sales' : sales_list, 'cum_sales' : cum_sales_list, 'distribution' : distributions})
    album_chart_df['date'] = date

    return album_chart_df


if __name__ == '__main__':

    # 연도별 앨범 판매량
    year_list = ['2022', '2023']
    album_chart_df_list = [get_yearly_album_chart(year) for year in year_list]
    yearly_album_chart_df = pd.concat(album_chart_df_list, ignore_index=True)

    print(yearly_album_chart_df)

    # 월별 앨범 판매량
    month_list = ['202401', '202402']
    album_chart_df_list = [get_monthly_album_chart(date) for date in month_list]
    monthly_album_chart_df = pd.concat(album_chart_df_list, ignore_index=True)

    print(monthly_album_chart_df)