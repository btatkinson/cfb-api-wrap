import pandas as pd
import numpy as np
import json

from pandas.io.json import json_normalize


with open('week12019.json') as f:
    data = json.load(f)


df = pd.io.json.json_normalize(data)

# df.to_csv('kentucky_toledo2019.csv',index=False)

df['game_id'] = df['home'] + '_' + df['away']
# # calculate time remaining in half
def tr_half(period, minutes, seconds):
    tr = 0
    if period in [1,3]:
        # add a quarter of time remaining
        tr += 900
    tr += (60 * minutes + seconds)
    return tr

def tr_game(period, minutes, seconds):
    quarters_left = 4-period
    added_secs = 15*60*quarters_left
    return (60*minutes + seconds + added_secs)

df['clock.seconds'] = df['clock.seconds'].fillna(0)
df['clock.minutes'] = df['clock.minutes'].fillna(0)

df['tr_half'] = df.apply(lambda row: tr_half(row['period'],row['clock.minutes'],row['clock.seconds']),axis=1)
df['tr_game'] = df.apply(lambda row: tr_game(row['period'],row['clock.minutes'],row['clock.seconds']),axis=1)

games = df.groupby(['game_id'])['tr_half','tr_game']

errors = []
for game,game_plays in games:
    num_uniques = len(game_plays['tr_game'].unique())
    errors.append([game,num_uniques])

err_df = pd.DataFrame(errors,columns=['id','num_uniques'])

err_df.to_csv('week_1_errors.csv',index=False)









#
