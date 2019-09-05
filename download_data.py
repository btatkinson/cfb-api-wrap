import pandas as pd
import datetime
import json
import requests
import pathlib
import gc
gc.collect()

from pandas.io.json import json_normalize
from tqdm import tqdm

GL_PATH='./output/games.csv'
BASE_URL='https://api.collegefootballdata.com/'

def clean(games):

    # remove 2019
    games = games.loc[games['season']!=2019]

    # drop score NaNs
    games = games.dropna(subset=['home_points','away_points'])

    # replace nans with 0 in other two int columns
    games['attendance'] = games['attendance'].fillna(0)
    games['venue_id'] = games['venue_id'].fillna(0)

    int_cols = ['attendance','away_points','home_points','venue_id']
    for ic in int_cols:
        games[ic] = games[ic].astype(int)

    return games

def get_game_list():
    games = pd.read_csv(GL_PATH)

    games = clean(games)

    return games

def get_years(game_list):
    return list(game_list.season.unique())

def reg_post(game_list):
    return list(game_list.season_type.unique())

def get_weeks(game_list, years):
    return list(game_list.week.unique())

def get_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def get_pbp(year, season_type, week):
    api = BASE_URL
    url_append = 'plays?seasonType='+str(season_type)+'&year='+str(year)+'&week='+str(week)
    req_url = api + url_append
    json = get_url(req_url)
    df = json_normalize(json)
    return df

def get_drives(year, season_type, week):
    api = BASE_URL
    url_append = 'drives?seasonType='+str(season_type)+'&year='+str(year)+'&week='+str(week)
    req_url = api + url_append
    json = get_url(req_url)
    df = json_normalize(json)
    return df

def save_pbp(pbp, year):
    dir = './output/'+str(year)+'/'
    # create directory if it doesn't exist
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
    file_path = dir + str(year)+'_pbp.csv'
    pbp.to_csv(file_path, index=False)
    return

def save_drives(pbp, year):
    dir = './output/'+str(year)+'/'
    # create directory if it doesn't exist
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
    file_path = dir + str(year)+'_drives.csv'
    pbp.to_csv(file_path, index=False)
    return

def add_time(pbp, year, season_type, week):
    pbp['season'] = year
    pbp['week'] = week
    pbp['season_type'] = season_type

    return pbp

if __name__ == "__main__":
    game_list = get_game_list()

    years = get_years(game_list)
    # see if regular season or postseason is in data
    reg_post = reg_post(game_list)
    weeks = get_weeks(game_list, years)

    for year in years:
        print('GATHERING ' + str(year) + ' SEASON PLAY BY PLAY DATA')
        season_pbp = pd.DataFrame()
        season_drives = pd.DataFrame()
        for rp in reg_post:
            if rp == 'regular':
                for week in tqdm(weeks):
                    season_type = 'regular'
                    week_pbp = get_pbp(year, season_type, week)
                    week_pbp = add_time(week_pbp, year, season_type, week)
                    season_pbp = pd.concat([season_pbp, week_pbp],sort=False)
                    if 'start_time.hours' in list(season_pbp):
                        season_pbp = season_pbp.drop(columns=['start_time.hours','end_time.hours'])
                    drives = get_drives(year,season_type,week)
                    if 'start_time.hours' in list(drives):
                        drives = drives.drop(columns=['start_time.hours','end_time.hours'])
                    season_drives = pd.concat([season_drives,drives],sort=False)

            else:
                week = 1
                season_type = 'postseason'
                post_pbp = get_pbp(year, season_type, week)
                post_pbp = add_time(post_pbp, year, season_type, week)
                if 'start_time.hours' in list(post_pbp):
                    post_pbp = post_pbp.drop(columns=['start_time.hours','end_time.hours'])
                season_pbp = pd.concat([season_pbp, post_pbp],sort=False)
                post_drives = get_drives(year,season_type,week)
                if 'start_time.hours' in list(post_drives):
                    post_drives = post_drives.drop(columns=['start_time.hours','end_time.hours'])
                season_drives = pd.concat([season_drives,post_drives],sort=False)

        save_pbp(season_pbp, year)
        save_drives(season_drives, year)








#
