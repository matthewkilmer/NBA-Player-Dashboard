# NBA-Player-Dashboard

## Overview
This project aims to create an NBA player statistics page using game data. The player game logs are pulled using the NBA API, stored in a relational database, then aggregated into season and split data that updates automatically as new games are played. The application will be an interactive Streamlit dashboard that allows for the user to explore game-level and season-level data for all active players.

The goal of this project is to demonstrate the ability to perform data collection, cleaning, storage, aggregation, and presentation through an interactive dashboard.

## Data Sources
- nba_api: NBA stats API used to collect game data and metadata for the 2025-26 NBA season.

## Project Architecture

### Workflow
1. Pull raw player gamelogs from the NBA API.
2. Clean data an store in a MySQL database.
3. Aggregate per-game datas into season-level stats and splits.
4. Create an interactive Streamlit dashboard to present the results.

### Table Designs
1. players

2. player_game_logs

3. player_season_summary

4. player_season_splits

## Tools Used
 - Python
 - nba_api
 - Streamlit
 - Pandas
 - MySQL Workbench
 - SQL




