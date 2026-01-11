### THIS SCRIPT CLEANS THE RAW GAMELOGS PULLED FROM THE API AND FORMATS THEM FOR DB INSERTION
## Import libraries
from pull_data import pull_gamelogs
import pandas as pd

## Define a function to clean the data to make it ready for storage.
def clean_gamelogs(raw_df):

    # make a copy of the df to perserve the original
    df = raw_df.copy()
    
    # convert dates to datetime
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])

    # make sure our statistical columns are numeric
    num_cols = [
        'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
        'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL',
        'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS'
    ]

    # handle missing data
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # derive home/away and opponent from matchup
    df['TEAM'] = df['MATCHUP'].apply(lambda x: x.split(' ')[0])
    df['HOME_AWAY'] = df['MATCHUP'].apply(lambda x: 'A' if '@' in x else 'H')
    df['OPPONENT'] = df['MATCHUP'].apply(lambda x: x.split(' ')[-1])

    # rename Game_id to match the capitalization of all columns
    df = df.rename(columns={'Game_ID':'GAME_ID'})

    # reorder the columns to match the sql table schema
    mapped_cols = [
        'PLAYER_ID', 'SEASON_ID', 'GAME_ID', 'GAME_DATE',
        'TEAM', 'OPPONENT', 'HOME_AWAY', 'WL',
        'MIN', 'PTS',
        'FGM', 'FGA', 'FG_PCT',
        'FG3M', 'FG3A', 'FG3_PCT',
        'FTM', 'FTA', 'FT_PCT',
        'OREB', 'DREB', 'REB',
        'AST', 'STL', 'BLK',
        'TOV', 'PF', 'PLUS_MINUS'
    ]
    

    # print statement to signify cleaning is complete
    print(f'Logs for {len(df)} players successfully completed.')
    return df[mapped_cols]

## Define a function to clean all player metadata
def clean_metadata(raw_df):

    # make a copy of the df to perserve the original
    df = raw_df.copy()

    # convert birthdate to datetime
    df['DOB'] = pd.to_datetime(df['DOB'], errors='coerce')

    # handle missing values
    df['WEIGHT'] = pd.to_numeric(df['WEIGHT'], errors='coerce')
    df['DRAFT_YEAR'] = pd.to_numeric(df['DRAFT_YEAR'], errors='coerce')
    df['DRAFT_ROUND'] = pd.to_numeric(df['DRAFT_ROUND'], errors='coerce')
    df['DRAFT_NUMBER'] = pd.to_numeric(df['DRAFT_NUMBER'], errors='coerce')

    df['POSITION'] = df['POSITION'].fillna('Unknown')
    df['COUNTRY'] = df['COUNTRY'].fillna('Unknown')

    # remove duplicates
    df = df.drop_duplicates(subset=['PLAYER_ID'])

    # print a statment once cleaning is complete
    print(f'Metadata for {len(df)} players successfully cleaned.')
    return df

