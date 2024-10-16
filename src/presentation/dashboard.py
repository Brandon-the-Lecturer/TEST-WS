# Dependencies
import streamlit as st

import data.play_by_play as DataService_PBP 
import data.drives as DataService_Drives 
import logic.pbp as LogicService

# Variables
SEASON_MAX = 2024
SEASON_MIN = 1994

GAME_WEEK_MIN = 1
GAME_WEEK_MAX = 17

GAMES = ["KC@BAL", "SF@TEN"]

TEAM_SELECTION_SPLIT_CHAR = "-at-"
SCOUTING_SIDES = ["Visitors", "Home"]
SIDE_BAR_HEADER = "Game Selection".upper()
SIDE_BAR_BUTTON_NAME = "Bestätigen"

# Function

def display_game(raw:str) -> str:
    return raw.upper().replace("-AT-", " at ")

def main():
    # Header
    st.set_page_config(page_title="Game Scout Report", page_icon="🏈")

    # Sidebar
    with st.sidebar:
        st.header(SIDE_BAR_HEADER)
        
        selected_season = st.selectbox(label="Season", options=DataService_PBP.get_seasons())
        selected_week = st.selectbox(label="Week", options=DataService_PBP.get_week_of_season(season=selected_season))
        selected_game = st.selectbox(label="Game", options=DataService_PBP.get_game_of_week(week=selected_week, season=selected_season), format_func=display_game)
        

        team_selection = selected_game.split(TEAM_SELECTION_SPLIT_CHAR)
        scout_team = st.radio(label="Team to scout", options=team_selection)
        
        if DataService_Drives.check_for_data(selected_season, selected_week, scout_team):
            st.success("Daten vollständig")
        else: 
            st.error("Daten unvollständig")
    
    
    if st.sidebar.button(SIDE_BAR_BUTTON_NAME):
        

        # Main Body
        st.header(f"Scout Report for {scout_team}")
        st.write(f"Selected Season: {selected_season}")
        st.write(f"Selected Week: {selected_week}")
        st.write(f"Selected Game: {selected_game}")
        

        with st.expander("Data Product Type 1: Raw Data"):            
            pbp_data = DataService_PBP.get_pbp_data(selected_season, selected_week, selected_game)
            st.write(pbp_data)
        
        with st.expander("Data Product Type 2: Aggregates Data"):
            pbp_data_with_pos = LogicService.get_pbp_data(selected_season, selected_week, selected_game)
            st.write(pbp_data_with_pos)
        
        with st.expander("Data Product Type 3: Algorithm"):
            st.write("Yo")
        
        with st.expander("Data Product Type 4: Supported Decision"):
            st.write("Yo")
        
        with st.expander("Data Product Type 5: Automated Decision"):
            st.write("Yo")

    

# Program
if __name__ == "__main__":
    main()
