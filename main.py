import json

from album_module.last_fm_api import LastFm

if __name__ == '__main__':

    with open('account_info\last_fm_account_info.json', 'r') as file:
        last_fm_acc_info = json.load(file)

    last_fm = LastFm(acc_info=last_fm_acc_info)

    artist_list = last_fm.get_artist_list(artist_cnt=100, tag='k-pop', artist_list=['Seventeen', 'NewJeans', 'aespa', 'LE SSERAFIM', 'Kiss Of Life', 'Illit'])

    print(artist_list)

    album_info_df = last_fm.get_album_info(multi_mode=True)
    print(album_info_df)