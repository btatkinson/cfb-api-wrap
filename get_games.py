import pandas as pd
import numpy as np

import datetime
import json
import requests

from pandas.io.json import json_normalize
from tqdm import tqdm

# init
this_year = int(datetime.datetime.now().year)

# games go back far
# but play by play is capable of 2002-present
SETTINGS = {
    "years":list(range(2002, this_year+1)),
    "regseason":True,
    "postseason":True
}
API_URL = 'https://api.collegefootballdata.com/games'


def get_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def get_games():
    years = SETTINGS["years"]
    reg = SETTINGS["regseason"]
    post = SETTINGS["postseason"]
    api = API_URL

    years=[2018]

    for year in tqdm(years):
        # initialize
        reg_json = pd.DataFrame()
        post_json = pd.DataFrame()

        if reg:
            url_append = '?year='+str(year)+'&seasonType=regular'
            req_url = api + url_append
            reg_json = get_url(req_url)
            reg_df = json_normalize(reg_json)
            print(len(reg_df))

        if post:
            url_append = '?year='+str(year)+'&seasonType=postseason'
            req_url = api + url_append
            post_json = get_url(req_url)
            post_df = json_normalize(post_json)
            print(len(post_df))

        if (len(reg_df) > 0) and (len(post_df) > 0):
            df = pd.concat([reg_df,post_df])
        elif len(reg_df) > 0:
            df = reg_df
        else:
            df = post_df

        return df

    return None

def save_games():
    pass

if __name__ == "__main__":
    games = get_games()
    save_games(games)
