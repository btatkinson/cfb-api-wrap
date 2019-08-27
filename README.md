# Python Wrapper for College Football Data API

API documentation: https://api.collegefootballdata.com/api/docs/?url=/api-docs.json

Required Python packages:
  requests
  tqdm (not an absolute must--can remove it from code if desired)


### Usage:

To get a list of games, along with venue and date information, run ``` python3 get_games.py ```
If you want to adjust postseason/reg season, or pick what seasons you want, adjust SETTINGS in get_games python file. You can also change the output directory.

The file ``` play_by_play.py ``` will look for games.csv in the output directory. It will load a list of game ids from that file. Once it has that list, it will get play by play information for all of those games. WARNING! That's a lot of data. I currently have it sorted into seasons in the output file.







<!-- end -->
