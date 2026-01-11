### THIS SCRIPT EXECUTES THE ENTIRE PIPELINE OF PULLING GAMELOGS, CLEANING THEM, AND INSERTING THEM INTO OUR DB
## Import libraries
from db_connection import connect_to_db
from pull_data import pull_gamelogs, pull_metadata
from clean_data import clean_gamelogs, clean_metadata
from db_insert import insert_gamelogs, insert_player_metadata

## Define and run our main function
if __name__ == '__main__':

    #raw_metadata = pull_metadata()
    #metadata_df = clean_metadata(raw_metadata)
    #insert_player_metadata(metadata_df)

    raw_gamelogs = pull_gamelogs(season='ALL', sleep_time=3)
    gamelogs_df = clean_gamelogs(raw_gamelogs)
    insert_gamelogs(gamelogs_df)
