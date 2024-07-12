import musicbrainzngs

import json

import pandas as pd
import numpy as np

import parmap

from auto_tqdm import tqdm

import sys
sys.path.append(r'C:\lucio 서강대 정보통신대학원\학위논문\project')
from runtime_check import how_long

# musicbrainz user agent 설정
with open('account_info\musicbrainz_account_info.json', 'r') as file: musicbrainz_acc_info = json.load(file)
musicbrainzngs.set_useragent(
                        musicbrainz_acc_info['application_name'],
                        musicbrainz_acc_info['version'],
                        musicbrainz_acc_info['mail']
                    )

NUM_POOL = 6 # multi processing 실행할 코어 수


def get_artist_info(artist_name: str) -> dict:
    '''아티스트 정보 가져옴

        @Args:
            -artist_name: 아티스트 명

        @Returns:
            -artist_info_dic: 아티스트 상세 정보 딕셔너리
    '''

    result = musicbrainzngs.search_artists(artist=artist_name)
    artist_info = result['artist-list'][0]

    # 데뷔일
    debut_date = artist_info['life-span']['begin']

    # 그룹 속성
    artist_types = [artist_type['name'] for artist_type in artist_info['tag-list']]

    # 멤버 수, 유닛 수
    artist_id = artist_info['id']
    artist_member_label_info = musicbrainzngs.get_artist_by_id(artist_id, includes=['artist-rels', 'label-rels'])

    artist_member_info = [artist_member['artist'] for artist_member in artist_member_label_info['artist']['artist-relation-list']]
    member_cnt = len([member for member in artist_member_info if member['type'] == 'Person'])
    sub_group_cnt = len([member for member in artist_member_info if member['type'] == 'Group'])

    # 소속사
    try:
        artist_label_info = [artist_label['label'] for artist_label in artist_member_label_info['artist']['label-relation-list']]
        artist_label = artist_label_info[0]['name']

    except:
        artist_label = None

    artist_info_dic = {}
    artist_info_dic['artist_name'] = artist_name
    artist_info_dic['artist_id'] = artist_id
    artist_info_dic['debut_date'] = debut_date
    artist_info_dic['artist_types'] = artist_types
    artist_info_dic['member_cnt'] = member_cnt
    artist_info_dic['sub_group_cnt'] = sub_group_cnt
    artist_info_dic['label'] = artist_label

    return artist_info_dic


def _get_single_album_info(album_id: str) -> dict:
    '''단일 앨범 정보 가져옴

        @Args:
            -album_id: 앨범 id

        @Returns:
            -single_album_info_dic: 앨범 상세 정보 딕셔너리

        @Comment:
            - 앨범 타입이 정규, 싱글, EP 또는 mini 인 경우에만 가져오도록 조건 추가
    '''

    single_album_info = musicbrainzngs.get_release_by_id(album_id, includes=["recordings", "artists", "labels", "release-groups"])['release']

    # title
    album_title = single_album_info['title']

    # 앨범 타입
    album_type = single_album_info['release-group']['primary-type']

    # 장르 정보
    genres = single_album_info.get('tag-list', [])
    main_genre = genres[0]['name'] if genres else None
    sub_genres = [genre['name'] for genre in genres[1:]] if len(genres) > 1 else None

    # 발매일
    release_date = single_album_info['date']

    # 트랙 수 & 평균 재생 시간
    track_cnt = single_album_info['medium-list'][0]['track-count']

    try:
        track_avg_play = np.mean([int(track['length']) for track in single_album_info['medium-list'][0]['track-list']])

    except:
        track_avg_play = None

    single_album_info_dic = {}
    single_album_info_dic['album_id'] = album_id; single_album_info_dic['album_name'] = album_title
    single_album_info_dic['album_type'] = album_type; single_album_info_dic['release_date'] = release_date
    single_album_info_dic['main_genre'] = main_genre; single_album_info_dic['sub_genre'] = sub_genres
    single_album_info_dic['track_cnt'] = track_cnt; single_album_info_dic['avg_track_play_time'] = track_avg_play

    return single_album_info_dic


def get_album_info(artist_id: str) -> pd.DataFrame:
    '''특정 아티스트의 모든 앨범 정보 취합

        @Args:
            -artist_id: 아티스트 id

        @Returns:
            -album_info_df: 아티스트의 모든 앨범 상세 정보 데이터프레임
    '''

    result = musicbrainzngs.get_artist_by_id(artist_id, includes=["release-groups"])

    albums = result['artist']['release-group-list']

    # 조회된 album 그룹 중 첫 번째 앨범명 데이터 가져옴 (동일한 앨범명 여러 개 존재)
    albums = [musicbrainzngs.get_release_group_by_id(album['id'], includes=['releases'])['release-group']['release-list'][0] for album in albums]
    album_ids = [album['id'] for album in albums]

    # 앨범 상세 정보
    album_info_dic = parmap.map(
                            _get_single_album_info,
                            album_ids,
                            pm_pbar=True,
                            pm_processes=NUM_POOL
                        )
    
    album_info_df = pd.DataFrame(album_info_dic)

    return album_info_df


def get_event_info(artist_id) -> pd.DataFrame:
    '''특정 아티스트의 공연, 방송 정보 취합

        @Args:
            -artist_id: 아티스트 id

        @Returns:
            -artist_event_df: 아티스트의 공연 및 방송 상세 정보 데이터프레임
    '''
    
    artist_event_info = musicbrainzngs.get_artist_by_id(artist_id, includes=['event-rels'])['artist']['event-relation-list']

    artist_event_dic_list = []
    for events in artist_event_info:

        artist_event_dic = {}

        # 아티스트 행사 참여 수준
        participant_type = events['type']

        # 행사명 및 종류
        event_type = events['event']['type']; event_name = events['event']['name']

        # 행사 시작 및 종료일
        event_start_date = events['event']['life-span']['begin']; event_end_date = events['event']['life-span']['end']

        artist_event_dic['participant_type'] = participant_type
        artist_event_dic['event_name'] = event_name
        artist_event_dic['event_type'] = event_type
        artist_event_dic['event_begin_date'] = event_start_date
        artist_event_dic['event_end_date'] = event_end_date

        artist_event_dic_list.append(artist_event_dic)

    artist_event_df = pd.DataFrame(artist_event_dic_list)

    return artist_event_df


@how_long
def concat_artist_info(artist_list: list) -> pd.DataFrame:
    '''아티스트 상세 정보 모두 취합

        @Args:
            -artist_list: 아티스트 리스트

        @Returns:
            -artist_album_df: 아티스트 상세 정보 데이터프레임

        @Comment:
            - 아티스트 공연 event 정보 추가
    '''

    # 아티스트 기본 정보
    artist_info_dic = parmap.map(
                                get_artist_info,
                                artist_list,
                                pm_pbar=False,
                                pm_processes=NUM_POOL
                            )
    
    artist_info_df = pd.DataFrame(artist_info_dic)

    # 앨범 상세 및 공연 이벤트 정보
    album_info_df_list = []; event_info_df_list = []
    for artist_name, artist_id in zip(artist_info_df['artist_name'].unique(), artist_info_df['artist_id'].unique()):

        print(f'<<<<<<<<<<< {artist_name} >>>>>>>>>>>>')

        # 1. 아티스트 앨범 정보
        album_info_df = get_album_info(artist_id)
        album_info_df['artist_id'] = artist_id
        album_info_df_list.append(album_info_df)

        # 2. 공연, 방송 이벤트 정보
        event_info_df = get_event_info(artist_id)
        event_info_df['artist_id'] = artist_id
        event_info_df_list.append(event_info_df)

    album_info_df = pd.concat(album_info_df_list)
    event_info_df = pd.concat(event_info_df_list)

    # 최종 데이터 병합
    artist_album_df = pd.merge(artist_info_df, album_info_df, on='artist_id', how='inner').merge(event_info_df, on='artist_id', how='inner')

    return artist_album_df
    

if __name__ == '__main__':

    '''
        Available includes:
        recordings, releases, release-groups, works, various-artists, discids, media, isrcs, aliases, annotation, area-rels, artist-rels, label-rels, 
        place-rels, event-rels, recording-rels, release-rels, release-group-rels, series-rels, url-rels, work-rels, instrument-rels, tags, user-tags, 
        ratings, user-ratings
    '''

    artist_list = ['SEVENTEEN', 'BTS', 'Stray Kids', 'NCT DREAM', 'TOMORROW X TOGETHER', 'IVE', 'aespa', 'NewJeans', 'TWICE', 'BLACKPINK']

    artist_info_df = concat_artist_info(artist_list)
    print(artist_info_df)
    # artist_info_df.to_csv('top5_group_info.csv', encoding='utf-8-sig')