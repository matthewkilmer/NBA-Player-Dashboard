# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from src.db_connection import connect_to_db

# Page config
st.set_page_config(
    page_title="NBA Player Stats Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_connection():
    return connect_to_db()

# Data loading functions
@st.cache_data(ttl=600)
def get_all_players():
    """Get all players with career stats"""
    conn = get_connection()
    query = """
        SELECT * FROM PLAYER_CAREER_STATS 
        WHERE GP > 0
        ORDER BY PLAYER_NAME
    """
    df = pd.read_sql(query, conn)
    return df

@st.cache_data(ttl=600)
def get_player_metadata(player_id):
    """Get player metadata"""
    conn = get_connection()
    query = f"""
        SELECT * FROM PLAYER_METADATA 
        WHERE PLAYER_ID = {player_id}
    """
    df = pd.read_sql(query, conn)
    return df.iloc[0] if not df.empty else None

@st.cache_data(ttl=600)
def get_player_career_stats(player_id):
    """Get career stats for a player"""
    conn = get_connection()
    query = f"""
        SELECT * FROM PLAYER_CAREER_STATS 
        WHERE PLAYER_ID = {player_id}
    """
    df = pd.read_sql(query, conn)
    return df.iloc[0] if not df.empty else None

@st.cache_data(ttl=600)
def get_player_seasons(player_id):
    """Get season-by-season stats"""
    conn = get_connection()
    query = f"""
        SELECT * FROM PLAYER_SEASON_STATS 
        WHERE PLAYER_ID = {player_id}
        ORDER BY SEASON_ID DESC
    """
    df = pd.read_sql(query, conn)
    return df

@st.cache_data(ttl=600)
def get_recent_games(player_id, num_games=10):
    """Get most recent N games"""
    conn = get_connection()
    query = f"""
        SELECT 
            GAME_DATE,
            TEAM,
            OPPONENT,
            HOME_AWAY,
            WL,
            MIN,
            PTS,
            REB,
            AST,
            STL,
            BLK,
            TOV,
            FGM,
            FGA,
            FG_PCT,
            FG3M,
            FG3A,
            FG3_PCT,
            FTM,
            FTA,
            FT_PCT,
            PLUS_MINUS
        FROM PLAYER_GAME_LOGS
        WHERE PLAYER_ID = {player_id}
        ORDER BY GAME_DATE DESC
        LIMIT {num_games}
    """
    df = pd.read_sql(query, conn)
    return df

@st.cache_data(ttl=600)
def get_career_highs(player_id):
    """Get career high performances"""
    conn = get_connection()
    query = f"""
        SELECT * FROM PLAYER_CAREER_HIGHS
        WHERE PLAYER_ID = {player_id}
    """
    df = pd.read_sql(query, conn)
    return df.iloc[0] if not df.empty else None

@st.cache_data(ttl=600)
def get_home_away_splits(player_id):
    """Get home vs away splits"""
    conn = get_connection()
    query = f"""
        SELECT 
            CASE 
                WHEN HOME_AWAY = 'H' THEN 'Home'
                WHEN HOME_AWAY = 'A' THEN 'Away'
                ELSE 'Unknown'
            END as LOCATION,
            COUNT(*) as GP,
            ROUND(AVG(MIN), 1) as MPG,
            ROUND(AVG(PTS), 1) as PPG,
            ROUND(AVG(REB), 1) as RPG,
            ROUND(AVG(AST), 1) as APG,
            ROUND(AVG(STL), 1) as SPG,
            ROUND(AVG(BLK), 1) as BPG,
            ROUND(SUM(FGM) / NULLIF(SUM(FGA), 0), 3) as FG_PCT,
            ROUND(SUM(FG3M) / NULLIF(SUM(FG3A), 0), 3) as FG3_PCT,
            ROUND(SUM(FTM) / NULLIF(SUM(FTA), 0), 3) as FT_PCT
        FROM PLAYER_GAME_LOGS
        WHERE PLAYER_ID = {player_id} AND HOME_AWAY IS NOT NULL
        GROUP BY HOME_AWAY
        ORDER BY HOME_AWAY
    """
    df = pd.read_sql(query, conn)
    return df

@st.cache_data(ttl=600)
def get_win_loss_splits(player_id):
    """Get win vs loss splits"""
    conn = get_connection()
    query = f"""
        SELECT 
            CASE 
                WHEN WL = 'W' THEN 'Wins'
                WHEN WL = 'L' THEN 'Losses'
                ELSE 'Unknown'
            END as RESULT,
            COUNT(*) as GP,
            ROUND(AVG(PTS), 1) as PPG,
            ROUND(AVG(REB), 1) as RPG,
            ROUND(AVG(AST), 1) as APG,
            ROUND(AVG(STL), 1) as SPG,
            ROUND(AVG(BLK), 1) as BPG,
            ROUND(SUM(FGM) / NULLIF(SUM(FGA), 0), 3) as FG_PCT,
            ROUND(AVG(PLUS_MINUS), 1) as AVG_PLUS_MINUS
        FROM PLAYER_GAME_LOGS
        WHERE PLAYER_ID = {player_id} AND WL IS NOT NULL
        GROUP BY WL
        ORDER BY WL DESC
    """
    df = pd.read_sql(query, conn)
    return df

@st.cache_data(ttl=600)
def get_season_trend(player_id):
    """Get season trend data for charts"""
    conn = get_connection()
    query = f"""
        SELECT 
            SEASON_ID,
            GP,
            PPG,
            RPG,
            APG,
            FG_PCT,
            FG3_PCT,
            FT_PCT
        FROM PLAYER_SEASON_STATS
        WHERE PLAYER_ID = {player_id}
        ORDER BY SEASON_ID
    """
    df = pd.read_sql(query, conn)
    return df

@st.cache_data(ttl=600)
def get_monthly_stats(player_id, season_id=None):
    """Get monthly performance"""
    conn = get_connection()
    
    season_filter = f"AND SEASON_ID = '{season_id}'" if season_id else ""
    
    query = f"""
        SELECT 
            YEAR(GAME_DATE) as YEAR,
            MONTH(GAME_DATE) as MONTH,
            DATE_FORMAT(GAME_DATE, '%Y-%m') as YEAR_MONTH,
            COUNT(*) as GP,
            ROUND(AVG(PTS), 1) as PPG,
            ROUND(AVG(REB), 1) as RPG,
            ROUND(AVG(AST), 1) as APG
        FROM PLAYER_GAME_LOGS
        WHERE PLAYER_ID = {player_id} {season_filter}
        GROUP BY YEAR(GAME_DATE), MONTH(GAME_DATE), DATE_FORMAT(GAME_DATE, '%Y-%m')
        ORDER BY YEAR_MONTH
    """
    df = pd.read_sql(query, conn)
    return df

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🏀 NBA Player Stats Dashboard</h1>', unsafe_allow_html=True)
    
    # Load all players
    players_df = get_all_players()
    
    if players_df.empty:
        st.error("No player data found. Please run the data pipeline first.")
        return
    
    # Sidebar - Player selection and filters
    with st.sidebar:
        st.header("🔍 Player Selection")
        
        # Search/filter options
        search_term = st.text_input("Search player name", "")
        
        # Filter players based on search
        if search_term:
            filtered_players = players_df[
                players_df['PLAYER_NAME'].str.contains(search_term, case=False, na=False)
            ]
        else:
            filtered_players = players_df
        
        # Sort options
        sort_by = st.selectbox(
            "Sort by",
            ["Name (A-Z)", "PPG (High to Low)", "RPG (High to Low)", "APG (High to Low)"]
        )
        
        if sort_by == "Name (A-Z)":
            filtered_players = filtered_players.sort_values('PLAYER_NAME')
        elif sort_by == "PPG (High to Low)":
            filtered_players = filtered_players.sort_values('PPG', ascending=False)
        elif sort_by == "RPG (High to Low)":
            filtered_players = filtered_players.sort_values('RPG', ascending=False)
        elif sort_by == "APG (High to Low)":
            filtered_players = filtered_players.sort_values('APG', ascending=False)
        
        # Player selection
        player_name = st.selectbox(
            "Select Player",
            options=filtered_players['PLAYER_NAME'].tolist(),
            index=0
        )
        
        st.markdown("---")
        
        # Display count
        st.caption(f"Showing {len(filtered_players)} of {len(players_df)} players")
    
    # Get selected player data
    player_career = players_df[players_df['PLAYER_NAME'] == player_name].iloc[0]
    player_id = int(player_career['PLAYER_ID'])
    player_meta = get_player_metadata(player_id)
    
    # ========================================
    # SECTION 1: PLAYER OVERVIEW
    # ========================================
    st.header("📊 Player Overview")
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        # Player headshot
        st.image(
            f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png",
            width=200
        )
    
    with col2:
        st.subheader(player_name)
        if player_meta is not None:
            st.write(f"**Position:** {player_meta['POSITION']}")
            st.write(f"**Height:** {player_meta['HEIGHT']}")
            st.write(f"**Weight:** {player_meta['WEIGHT']} lbs")
            if pd.notna(player_meta['DOB']):
                dob = pd.to_datetime(player_meta['DOB'])
                age = (datetime.now() - dob).days // 365
                st.write(f"**Age:** {age}")
            if pd.notna(player_meta['SCHOOL']) and player_meta['SCHOOL'] != 'Unknown':
                st.write(f"**College:** {player_meta['SCHOOL']}")
            st.write(f"**Seasons:** {player_career['SEASONS']}")
    
    with col3:
        st.metric("Games Played", f"{player_career['GP']}")
        st.metric("Minutes Per Game", f"{player_career['MPG']:.1f}")
    
    # Career averages
    st.subheader("Career Averages")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("PPG", f"{player_career['PPG']:.1f}")
    col2.metric("RPG", f"{player_career['RPG']:.1f}")
    col3.metric("APG", f"{player_career['APG']:.1f}")
    col4.metric("SPG", f"{player_career['SPG']:.1f}")
    col5.metric("BPG", f"{player_career['BPG']:.1f}")
    
    # Shooting percentages
    st.subheader("Career Shooting")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("FG%", f"{player_career['FG_PCT']:.1%}" if pd.notna(player_career['FG_PCT']) else "N/A")
    col2.metric("3P%", f"{player_career['FG3_PCT']:.1%}" if pd.notna(player_career['FG3_PCT']) else "N/A")
    col3.metric("FT%", f"{player_career['FT_PCT']:.1%}" if pd.notna(player_career['FT_PCT']) else "N/A")
    col4.metric("TS%", f"{player_career['TS_PCT']:.1%}" if pd.notna(player_career['TS_PCT']) else "N/A")
    col5.metric("eFG%", f"{player_career['EFG_PCT']:.1%}" if pd.notna(player_career['EFG_PCT']) else "N/A")
    
    st.markdown("---")
    
    # ========================================
    # SECTION 2: CAREER HIGHS
    # ========================================
    st.header("🔥 Career Highs")
    
    career_highs = get_career_highs(player_id)
    
    if career_highs is not None:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        col1.metric("Points", f"{int(career_highs['CAREER_HIGH_PTS'])}")
        col2.metric("Rebounds", f"{int(career_highs['CAREER_HIGH_REB'])}")
        col3.metric("Assists", f"{int(career_highs['CAREER_HIGH_AST'])}")
        col4.metric("Steals", f"{int(career_highs['CAREER_HIGH_STL'])}")
        col5.metric("Blocks", f"{int(career_highs['CAREER_HIGH_BLK'])}")
        col6.metric("3-Pointers", f"{int(career_highs['CAREER_HIGH_3PM'])}")
    else:
        st.info("No career high data available")
    
    st.markdown("---")
    
    # ========================================
    # SECTION 3: SEASON-BY-SEASON STATS
    # ========================================
    st.header("📅 Season-by-Season Stats")
    
    season_df = get_player_seasons(player_id)
    
    if not season_df.empty:
        # Display table
        st.dataframe(
            season_df[[
                'SEASON_ID', 'GP', 'MPG', 'PPG', 'RPG', 'APG', 
                'SPG', 'BPG', 'FG_PCT', 'FG3_PCT', 'FT_PCT'
            ]],
            use_container_width=True,
            hide_index=True
        )
        
        # Trend charts
        st.subheader("Performance Trends")
        
        trend_data = get_season_trend(player_id)
        
        if not trend_data.empty and len(trend_data) > 1:
            # Create tabs for different charts
            tab1, tab2, tab3 = st.tabs(["Scoring", "All Stats", "Shooting %"])
            
            with tab1:
                fig = px.line(
                    trend_data,
                    x='SEASON_ID',
                    y='PPG',
                    markers=True,
                    title='Points Per Game by Season'
                )
                fig.update_layout(xaxis_title="Season", yaxis_title="PPG")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=trend_data['SEASON_ID'], y=trend_data['PPG'], 
                                        mode='lines+markers', name='PPG'))
                fig.add_trace(go.Scatter(x=trend_data['SEASON_ID'], y=trend_data['RPG'], 
                                        mode='lines+markers', name='RPG'))
                fig.add_trace(go.Scatter(x=trend_data['SEASON_ID'], y=trend_data['APG'], 
                                        mode='lines+markers', name='APG'))
                fig.update_layout(
                    title='Stats Per Game by Season',
                    xaxis_title='Season',
                    yaxis_title='Per Game Average',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=trend_data['SEASON_ID'], y=trend_data['FG_PCT']*100, 
                                        mode='lines+markers', name='FG%'))
                fig.add_trace(go.Scatter(x=trend_data['SEASON_ID'], y=trend_data['FG3_PCT']*100, 
                                        mode='lines+markers', name='3P%'))
                fig.add_trace(go.Scatter(x=trend_data['SEASON_ID'], y=trend_data['FT_PCT']*100, 
                                        mode='lines+markers', name='FT%'))
                fig.update_layout(
                    title='Shooting Percentages by Season',
                    xaxis_title='Season',
                    yaxis_title='Percentage',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No season data available")
    
    st.markdown("---")
    
    # ========================================
    # SECTION 4: RECENT GAMES
    # ========================================
    st.header("🎯 Recent Games")
    
    num_games = st.slider("Number of games to show", 5, 20, 10)
    recent_games = get_recent_games(player_id, num_games)
    
    if not recent_games.empty:
        # Format the dataframe for display
        display_df = recent_games.copy()
        display_df['GAME_DATE'] = pd.to_datetime(display_df['GAME_DATE']).dt.strftime('%Y-%m-%d')
        display_df['MATCHUP'] = display_df.apply(
            lambda row: f"{row['TEAM']} {'vs' if row['HOME_AWAY'] == 'H' else '@'} {row['OPPONENT']}", 
            axis=1
        )
        
        # Show key stats
        st.dataframe(
            display_df[[
                'GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'PTS', 'REB', 'AST', 
                'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'PLUS_MINUS'
            ]],
            use_container_width=True,
            hide_index=True
        )
        
        # Recent games chart
        st.subheader("Recent Scoring Trend")
        fig = px.bar(
            recent_games.iloc[::-1],  # Reverse to show chronological
            x='GAME_DATE',
            y='PTS',
            color='WL',
            color_discrete_map={'W': 'green', 'L': 'red'},
            title=f'Last {num_games} Games - Points Scored'
        )
        fig.update_layout(xaxis_title="Game Date", yaxis_title="Points")
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent averages
        st.subheader(f"Last {num_games} Games Averages")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("PPG", f"{recent_games['PTS'].mean():.1f}")
        col2.metric("RPG", f"{recent_games['REB'].mean():.1f}")
        col3.metric("APG", f"{recent_games['AST'].mean():.1f}")
        col4.metric("FG%", f"{recent_games['FG_PCT'].mean():.1%}")
        col5.metric("+/-", f"{recent_games['PLUS_MINUS'].mean():.1f}")
    else:
        st.info("No recent game data available")
    
    st.markdown("---")
    
    # ========================================
    # SECTION 5: SPLITS
    # ========================================
    st.header("📊 Splits Analysis")
    
    tab1, tab2 = st.tabs(["Home vs Away", "Wins vs Losses"])
    
    with tab1:
        home_away = get_home_away_splits(player_id)
        
        if not home_away.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Statistics")
                st.dataframe(home_away, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("PPG Comparison")
                fig = px.bar(
                    home_away,
                    x='LOCATION',
                    y='PPG',
                    color='LOCATION',
                    title='Points Per Game: Home vs Away'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No home/away split data available")
    
    with tab2:
        win_loss = get_win_loss_splits(player_id)
        
        if not win_loss.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Statistics")
                st.dataframe(win_loss, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("PPG in Wins vs Losses")
                fig = px.bar(
                    win_loss,
                    x='RESULT',
                    y='PPG',
                    color='RESULT',
                    color_discrete_map={'Wins': 'green', 'Losses': 'red'},
                    title='Points Per Game: Wins vs Losses'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No win/loss split data available")
    
    # Footer
    st.markdown("---")
    st.caption(f"Data last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()