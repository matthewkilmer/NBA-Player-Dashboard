### THIS SCRIPT WILL INSERT THE CLEANED GAMELOGS INTO THE SQL DATABASE
## Import libraries
import mysql.connector
from db_connection import connect_to_db
import numpy as np

## Define a function to insert clean metadata into players
def insert_player_metadata(df):
    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = """
       INSERT INTO PLAYER_METADATA (
            PLAYER_ID, PLAYER_NAME, DOB,
            HEIGHT, WEIGHT, POSITION,
            DRAFT_YEAR, DRAFT_ROUND, DRAFT_NUMBER,
            SCHOOL, COUNTRY, HEADSHOT_URL
        )
        VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            PLAYER_NAME = VALUES(PLAYER_NAME),
            DOB = VALUES(DOB),
            HEIGHT = VALUES(HEIGHT),
            WEIGHT = VALUES(WEIGHT),
            POSITION = VALUES(POSITION),
            DRAFT_YEAR = VALUES(DRAFT_YEAR),
            DRAFT_ROUND = VALUES(DRAFT_ROUND),
            DRAFT_NUMBER = VALUES(DRAFT_NUMBER),
            SCHOOL = VALUES(SCHOOL),
            COUNTRY = VALUES(COUNTRY),
            HEADSHOT_URL = VALUES(HEADSHOT_URL),
            UPDATED_AT = CURRENT_TIMESTAMP;
    """

    df = df.replace({np.nan: None})

    data = []
    for _, row in df.iterrows():
        data.append((
            row['PLAYER_ID'], row['PLAYER_NAME'], row['DOB'], 
            row['HEIGHT'], row['WEIGHT'], row['POSITION'],
            row.get('DRAFT_YEAR'), row.get('DRAFT_ROUND'), row.get('DRAFT_NUMBER'),
            row.get('SCHOOL'), row.get('COUNTRY'), row['HEADSHOT_URL']
        ))

    cursor.executemany(insert_query, data)
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Inserted/Updated {len(df)} rows in players successfully!")

## Define a function to insert cleaned gamelogs
def insert_gamelogs(df):
    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = """
       INSERT INTO PLAYER_GAME_LOGS (
            PLAYER_ID, SEASON_ID, GAME_ID, GAME_DATE,
            TEAM, OPPONENT, HOME_AWAY, WL,
            MIN, PTS,
            FGM, FGA, FG_PCT,
            FG3M, FG3A, FG3_PCT,
            FTM, FTA, FT_PCT,
            OREB, DREB, REB,
            AST, STL, BLK,
            TOV, PF, PLUS_MINUS
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            TEAM = VALUES(TEAM),
            OPPONENT = VALUES(OPPONENT),
            HOME_AWAY = VALUES(HOME_AWAY),
            WL = VALUES(WL),
            MIN = VALUES(MIN),
            PTS = VALUES(PTS),
            FGM = VALUES(FGM),
            FGA = VALUES(FGA),
            FG_PCT = VALUES(FG_PCT),
            FG3M = VALUES(FG3M),
            FG3A = VALUES(FG3A),
            FG3_PCT = VALUES(FG3_PCT),
            FTM = VALUES(FTM),
            FTA = VALUES(FTA),
            FT_PCT = VALUES(FT_PCT),
            OREB = VALUES(OREB),
            DREB = VALUES(DREB),
            REB = VALUES(REB),
            AST = VALUES(AST),
            STL = VALUES(STL),
            BLK = VALUES(BLK),
            TOV = VALUES(TOV),
            PF = VALUES(PF),
            PLUS_MINUS = VALUES(PLUS_MINUS)
    """

    df = df.replace({np.nan: None})

    data = []
    for _, row in df.iterrows():
        data.append((
             row['PLAYER_ID'], row['SEASON_ID'], row['GAME_ID'], row['GAME_DATE'],
            row.get('TEAM'), row.get('OPPONENT'), row.get('HOME_AWAY'), row.get('WL'),
            row.get('MIN'), row.get('PTS'),
            row.get('FGM'), row.get('FGA'), row.get('FG_PCT'),
            row.get('FG3M'), row.get('FG3A'), row.get('FG3_PCT'),
            row.get('FTM'), row.get('FTA'), row.get('FT_PCT'),
            row.get('OREB'), row.get('DREB'), row.get('REB'),
            row.get('AST'), row.get('STL'), row.get('BLK'),
            row.get('TOV'), row.get('PF'), row.get('PLUS_MINUS')
        ))

    cursor.executemany(insert_query, data)
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Inserted/Updated {len(df)} rows in player_game_logs successfully!")
