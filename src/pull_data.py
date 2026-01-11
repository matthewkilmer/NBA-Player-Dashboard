### A SCRIPT TO PULL RAW NBA PLAYER GAME LOGS FOR 2025-26 SEASON, PLAYER METADATA, AND CAREER STATS
## Import libraries
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
import time
from datetime import datetime

## Define a function to pull game logs
def pull_gamelogs(season='ALL', sleep_time=3):

    print(f'Pulling game logs for all active players...')
    
    active_players = players.get_active_players()
    all_gamelogs = []

    for i, player in enumerate(active_players):
        player_id = player['id']
        player_name = player['full_name']

        try:
            gamelog = playergamelog.PlayerGameLog(
                player_id=player_id, 
                season=season
            ).get_data_frames()[0]
           
            if not gamelog.empty:
                gamelog['PLAYER_ID'] = player_id
                gamelog['PLAYER_NAME'] = player_name
                all_gamelogs.append(gamelog)
                print(f'Logs for {player_name} successfully retrieved ({i+1}/{len(active_players)})')
            
        except Exception as e:
            print(f'Unable to pull logs for {player_name}: {e}')

        time.sleep(sleep_time)

    if all_gamelogs:
        raw_df = pd.concat(all_gamelogs, ignore_index=True)
        print(f'\nSuccess! Retrieved {len(all_gamelogs)}/{len(active_players)} players')
        return raw_df
    else:
        print('\nNo game logs retrieved!')
        return pd.DataFrame()

def pull_metadata(sleep_time=1):
    
    active_players = players.get_active_players()
    metadata = []
    print('Pulling player metadata...')

    for i, player in enumerate(active_players):
        try:
            player_id = player['id']
            player_name = player['full_name']

            player_info = commonplayerinfo.CommonPlayerInfo(
                player_id=player_id
            ).get_data_frames()[0]
            
            # Extract raw data
            player_dict = {
                'PLAYER_ID': player_id,
                'PLAYER_NAME': player_name,
                'DOB': player_info.loc[0, 'BIRTHDATE'],
                'HEIGHT': player_info.loc[0, 'HEIGHT'],
                'WEIGHT': player_info.loc[0, 'WEIGHT'],
                'POSITION': player_info.loc[0, 'POSITION'],
                'DRAFT_YEAR': player_info.loc[0, 'DRAFT_YEAR'],
                'DRAFT_ROUND': player_info.loc[0, 'DRAFT_ROUND'],
                'DRAFT_NUMBER': player_info.loc[0, 'DRAFT_NUMBER'],
                'SCHOOL': player_info.loc[0, 'SCHOOL'],
                'COUNTRY': player_info.loc[0, 'COUNTRY'],
                'HEADSHOT_URL': f'https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png'
            }

            metadata.append(player_dict)
            print(f'Metadata for {player_name} successfully retrieved ({i+1}/{len(active_players)})')
            time.sleep(sleep_time)

        except Exception as e:
            print(f'Unable to pull metadata for {player_name}: {e}')

    print(f'\nMetadata retrieved for {len(metadata)} players')
    return pd.DataFrame(metadata)
