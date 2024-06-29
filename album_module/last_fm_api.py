import json
import pylast

import pandas as pd

import parmap

from auto_tqdm import tqdm

import sys
sys.path.append(r'C:\lucio 서강대 정보통신대학원\학위논문\project')
from runtime_check import how_long

class LastFm:

    def __init__(self, acc_info: dict) -> None:
        '''last.fm api 계정 생성자 초기화

            @Args:
                -acc_info: last.fm 계정 딕셔너리

            @Returns:
                -None
        '''
        self.network = pylast.LastFMNetwork(
                            api_key=acc_info['api_key'],
                            api_secret=acc_info['shared_secret'],
                            username=acc_info['user_name'],
                            password_hash=pylast.md5(acc_info['password'])
                        )
        
        
    def get_artist_list(self, artist_cnt=50, tag='all') -> list:
        '''전체 또는 특정 카테고리의 아티스트명 가져옴

            @Args:
                -artist_cnt: 가져올 아티스트 수

                -tag: 음악 카테고리

                -artist_list: 가져올 아티스트 그룹명 직접 지정 시 해당 args 사용

            @Returns:
                -top_artist_list: 아티스트 이름 리스트
        '''
        if tag == 'all':
            top_artists = self.network.get_top_artists(limit=artist_cnt)
            top_artist_list = [top_artist.item.name for top_artist in top_artists]

            return top_artist_list
        
        else:
            tag = pylast.Tag(tag, self.network)
            top_artist_list = [artist.item.name for artist in tag.get_top_artists(limit=artist_cnt)]

            return top_artist_list
            

    def _get_artist_album_info(self, artist_name: str, album_cnt: int) -> pd.DataFrame:
        '''단일 아티스트 앨범 정보 가져옴

            @Args:
                -artist_name: 아티스트 이름

                -album_cnt: 가져올 앨범 수

            @Returns:
                -single_artist_album_df: 단일 아티스트 앨범 상세 데이터
        '''
                    
        # 아티스트 객체 생성
        artist = self.network.get_artist(artist_name)

        # 아티스트의 앨범 목록 가져오기
        albums = artist.get_top_albums(limit=album_cnt)

        album_details_list = []
        for album_entry in albums:
            album = album_entry.item

            # 앨범 상세 정보 가져오기
            album_info = self.network.get_album(artist, album.title)

            try:
                # 앨범 정보 출력
                details = {
                    'artist' : artist_name,
                    'album' : album.title,
                    'playcount' : album_info.get_playcount(),
                    'listeners' : album_info.get_listener_count(),
                    'track_cnt' : len([track.title for track in album_info.get_tracks()])
                }

                album_details_list.append(details)

            except Exception as error:
                print(f'{error} in album name {album.title}')

        single_artist_album_df = pd.concat([pd.DataFrame(details, index=[0]) for details in album_details_list])

        return single_artist_album_df
    

    @how_long
    def get_album_info(self, top_artist_list: list, album_cnt=5, multi_mode=True):

        '''단일 아티스트 앨범 정보 병합 & 최종 앨범 정보 가져옴

            @Args:
                -top_artist_list: 앨범 정보 가져올 대상 아티스트 리스트

                -album_cnt: 가져올 앨범 수

            @Returns:
                -album_info_df: 아티스트 앨범 상세 데이터
        
        '''
        if multi_mode:
            single_artist_album_df = parmap.starmap(
                                            self._get_artist_album_info, 
                                            [(artist_name, album_cnt) for artist_name in top_artist_list],
                                            pm_pbar=True,
                                            pm_processes=6
                                        )

            album_info_df = pd.concat(single_artist_album_df, ignore_index=True)

            return album_info_df
        
        else:
            album_info_df_list = []
            for artist_name in tqdm(top_artist_list):
                single_artist_album_df = self._get_artist_album_info(artist_name, album_cnt)
                album_info_df_list.append(single_artist_album_df)

            album_info_df = pd.concat(album_info_df_list, ignore_index=True)

            return album_info_df


if __name__ == '__main__':

    with open('account_info\last_fm_account_info.json', 'r') as file:
        last_fm_acc_info = json.load(file)

    last_fm = LastFm(acc_info=last_fm_acc_info)

    # 1. 대상 아티스트 선언
    # artist_list = last_fm.get_artist_list(artist_cnt=5, tag='k-pop')
    artist_list = ['Seventeen', 'NewJeans', 'aespa', 'LE SSERAFIM', 'Kiss Of Life', 'Illit']
    print(artist_list)

    # 2. 아티스트 앨범 정보
    album_info_df = last_fm.get_album_info(top_artist_list=artist_list, album_cnt=10, multi_mode=True)
    print(album_info_df)