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
BASE_URL='https://api.collegefootballdata.com/plays'

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
    url_append = '?seasonType='+str(season_type)+'&year='+str(year)+'&week='+str(week)
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

def add_gameid(pbp, year, season_type, week):
    if 'home' in list(pbp):
        if season_type == 'regular':
            st = 'REG'
        elif season_type == 'postseason':
            st= 'POST'
        pbp['game_id'] = str(year) + st + str(week) + pbp['home'] +'v'+ pbp['away']
        pbp['game_id'] = pbp['game_id'].str.replace(" ","")
        pbp['game_id'] = pbp['game_id'].str.lower()
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
        for rp in reg_post:
            if rp == 'regular':
                for week in tqdm(weeks):
                    season_type = 'regular'
                    week_pbp = get_pbp(year, season_type, week)
                    week_pbp = add_gameid(week_pbp, year, season_type, week)
                    season_pbp = pd.concat([season_pbp, week_pbp])
            else:
                week = 1
                season_type = 'postseason'
                post_pbp = get_pbp(year, season_type, week)
                post_pbp = add_gameid(post_pbp, year, season_type, week)
                season_pbp = pd.concat([season_pbp, post_pbp])


        save_pbp(season_pbp, year)






#
