import pandas as pd
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
OUTPUT_PATH = './output/games.csv'


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

    # test
    # years=[2018]

    ay_df = pd.DataFrame()

    for year in tqdm(years):
        # initialize
        reg_json = pd.DataFrame()
        post_json = pd.DataFrame()

        if reg:
            url_append = '?year='+str(year)+'&seasonType=regular'
            req_url = api + url_append
            reg_json = get_url(req_url)
            reg_df = json_normalize(reg_json)

        if post:
            url_append = '?year='+str(year)+'&seasonType=postseason'
            req_url = api + url_append
            post_json = get_url(req_url)
            post_df = json_normalize(post_json)

        if (len(reg_df) > 0) and (len(post_df) > 0):
            df = pd.concat([reg_df,post_df])
        elif len(reg_df) > 0:
            df = reg_df
        else:
            df = post_df

        if len(ay_df) > 0:
            ay_df = pd.concat([ay_df,df])
        else:
            ay_df = df

    return ay_df



def save_games(games):
    games.to_csv(OUTPUT_PATH, index=False)
    return

if __name__ == "__main__":
    # GET request
    games = get_games()

    save_games(games)
