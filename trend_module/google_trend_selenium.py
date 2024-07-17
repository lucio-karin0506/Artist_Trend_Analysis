from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

import pandas as pd

import glob

def get_google_trend(search_keyword, periods):

    # 웹드라이버 설정
    driver = webdriver.Chrome()

    # 구글 트렌드 페이지 열기
    driver.get("https://trends.google.com/trends/")
    driver.implicitly_wait(30)
    driver.maximize_window()

    # 검색어 입력
    search_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="i7"]')))
    search_box.click()
    time.sleep(2)
    search_box.send_keys(search_keyword)

    # 검색어 두번째 drop down item (아티스트 그룹) 클릭
    # 드롭다운의 두 번째 아이템 선택
    time.sleep(5)
    dropdown_item = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div[4]/div[1]/c-wiz[1]/div/div[1]/div[3]/div/div[3]/ul/li[2]')))
    dropdown_category_text = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div[4]/div[1]/c-wiz[1]/div/div[1]/div[3]/div/div[3]/ul/li[2]/a/div/div[2]').text

    if dropdown_category_text in ['보이 그룹', '걸 그룹']:
        dropdown_item.click()

    else: # 검색어의 카테고리가 아티스트에 해당되지 않을 경우, 다시 검색
        driver.quit()
        get_google_trend(search_keyword, periods)

    # 설정한 기간 6개월씩 만큼 수행
    for start_date, end_date in periods:

        print((start_date, end_date))

        # 기간 설정
        # 1. '지난 1일' 드롭다운 UI 클릭 -> '맞춤 기간' drop down 클릭
        time.sleep(5)
        period_item = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="compare-pickers-wrapper"]/div/custom-date-picker')))
        period_item.click()

        time.sleep(2)
        dropdown_period_item = driver.find_element(By.ID, 'select_container_11')
        dropdown_period_item.find_element(By.ID, 'select_option_22').click()

        # 2. 시작 및 종료일 설정
        time.sleep(2)
        start_date_input = driver.find_element(By.CLASS_NAME, 'custom-date-picker-dialog-range-from').find_element(By.CLASS_NAME, 'md-datepicker-input-container > input')
        start_date_input.clear()
        start_date_input.send_keys(start_date)

        time.sleep(2)
        start_date_input = driver.find_element(By.CLASS_NAME, 'custom-date-picker-dialog-range-to').find_element(By.CLASS_NAME, 'md-datepicker-input-container > input')
        start_date_input.clear()
        start_date_input.send_keys(end_date)

        time.sleep(2)
        date_button = driver.find_elements(By.CLASS_NAME, 'custom-date-picker-dialog-button')[1]
        date_button.click()

        # 3. 데이터 다운로드
        try:
            time.sleep(10)
            download_button = driver.find_element(By.XPATH, '//*[@title="CSV"]')
            download_button.click()

        except:
            driver.refresh()
            time.sleep(10)
            download_button = driver.find_element(By.XPATH, '//*[@title="CSV"]')
            download_button.click()

    time.sleep(5)
    driver.quit()


def concat_google_trend():

    file_pattern = 'C:\\Users\\ameli\\Downloads\\multiTimeline*.csv'

    file_paths = glob.glob(file_pattern)

    artist_trend_df_list = []
    for file_path in file_paths:
        trend_df = pd.read_csv(file_path, skiprows=2)
        trend_df.columns = ['date', 'trend']
        trend_df['date'] = pd.to_datetime(trend_df['date'])

        artist_trend_df_list.append(trend_df)

    # 중복된 수집 기간 중 첫 번째 수집된 날짜만 가져옴
    artist_trend_df = pd.concat(artist_trend_df_list, ignore_index=True).drop_duplicates(subset=['date'], keep='first').sort_values('date')

    return artist_trend_df


if __name__ == '__main__':

    # 아티스트 구글 트렌드 정보 get
    search_keyword = 'IVE'
    periods = [
        ('2021. 11. 01', '2022. 05. 01'),
        ('2022. 05. 01', '2022. 11. 01'),
        ('2022. 11. 01', '2023. 05. 01')
    ]

    get_google_trend(search_keyword, periods)

    # 아티스트 구글 트렌드 정보 취합 및 저장
    artist_trend_df = concat_google_trend()

    start_date = (periods[0][0]).replace('. ', ''); end_date = (periods[-1][1]).replace('. ', '') # 최종 수집 기간
    artist_trend_df.to_csv(f'{search_keyword}_{start_date}_{end_date}_google_trend.csv')

    print(artist_trend_df)