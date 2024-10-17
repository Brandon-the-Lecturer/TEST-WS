# Dependencies
import matplotlib.pyplot as plt
import pandas as pd
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

GAME_STRING_SPLIT_CHAR = "-at-"
SCOUTING_SIDES = ["Visitors", "Home"]
SIDE_BAR_BUTTON_NAME = "Bestätigen"

# Function

def display_game(game_string:str) -> str:
    return game_string.replace("-at-", " at ")

def get_team_mapping(game_string:str) -> dict:
    teams = game_string.split(GAME_STRING_SPLIT_CHAR)
    return dict(zip(SCOUTING_SIDES, teams))

def get_line_plot_for_points_per_play(team_map: dict, df: pd.DataFrame, display_selection: str):
        
    # Daten in zwei Gruppen aufteilen
    visitors_possession = df[df['Possession'] == team_map["Visitors"]]
    home_possessions = df[df['Possession'] == team_map["Home"]]
    
    visitors_team = team_map["Visitors"].upper()
    home_team = team_map["Home"].upper()


    # Definierte Farben und Linienstile
    visitors_team_color = 'red'
    home_team_color = 'black'
    dashed_style = '--'  # Gestrichelte Linie für xP

    # Erstelle den Plot
    fig, ax = plt.subplots(figsize=(12, 6))

    if (display_selection == team_map["Visitors"]) | (display_selection == "Both"):
        # Plot für das First Possession Team
        ax.plot(
            visitors_possession.index,
            visitors_possession['xP_cum'],
            label=f"{visitors_team} xP",
            color=visitors_team_color, 
            linestyle=dashed_style
        )
        
        ax.plot(
            visitors_possession.index, 
            visitors_possession["Visitors"],
            label=f"{visitors_team} Score", 
            color=visitors_team_color
        )

    if (display_selection == team_map["Home"]) | (display_selection == "Both"):
        # Plot für das Other Possession Team
        ax.plot(
            home_possessions.index, 
            home_possessions['xP_cum'],
            label=f"{home_team} xP", 
            color=home_team_color, 
            linestyle=dashed_style
        )
        
        ax.plot(
            home_possessions.index, 
            home_possessions["Home"],
            label=f"{home_team} Score", 
            color=home_team_color
        )

    # Labels und Titel hinzufügen
    ax.set_xlabel("Play")
    ax.set_ylabel("Points")
    ax.set_title("Score & xP")
    ax.legend()
    ax.grid(True)

    return fig


def main():
    # Header
    st.set_page_config(page_title="Game Scout Report", page_icon="🏈")

    # Session
    # Definiere einen eindeutigen Schlüssel für den Button
    button_key = 'sidebar_button_pressed'

    # Initialisiere den session_state für den Button, falls er noch nicht existiert
    if button_key not in st.session_state:
        st.session_state[button_key] = False

    # Sidebar
    with st.sidebar:
        st.header("GAME SELECTION")
        
        selected_season = st.selectbox(label="Season", options=DataService_PBP.get_seasons())
        selected_week = st.selectbox(label="Week", options=DataService_PBP.get_week_of_season(season=selected_season))
        selected_game = st.selectbox(label="Game", options=DataService_PBP.get_game_of_week(week=selected_week, season=selected_season), format_func=display_game)
        

        team_map = get_team_mapping(selected_game)

        scout_team = st.radio(label="Team to scout", options=team_map.values())
        
        if DataService_Drives.check_for_data(selected_season, selected_week, scout_team):
            st.success("Daten vollständig")
            if st.button(SIDE_BAR_BUTTON_NAME):
                st.session_state[button_key] = True
        else: 
            st.error("Daten unvollständig")
    
    
    if st.session_state[button_key]:
        
        # Main Body
        st.header(f"Scout Report for {scout_team.upper()}")
        header_col1, header_col2, header_col3, header_col4 = st.columns(4)
        header_col1.metric(label="Season", value=selected_season)
        header_col2.metric(label="Week", value=selected_week)
        header_col3.metric(label="Visitors", value=team_map["Visitors"].upper())
        header_col4.metric(label="Home", value=team_map["Home"].upper())


        

        with st.expander("Data Product Type 1: Raw Data"):            
            pbp_data = LogicService.get_pbp_data(selected_season, selected_week, selected_game)
            st.write(pbp_data)
        
        with st.expander("Data Product Type 2: Aggregated Data"):
            pbp_data_with_pos = LogicService.get_pbp_data_agg(selected_season, selected_week, selected_game)
            st.write(pbp_data_with_pos)
        
        with st.expander("Data Product Type 3: Algorithm"):
            pbp_data_with_xp = LogicService.get_pbp_data_with_xp(selected_season, selected_week, selected_game)
            st.write(pbp_data_with_xp)
        
        with st.expander("Data Product Type 4: Supported Decision"):
            display_selection = st.radio("Selection", options=[*team_map.values(), "Both"], index=2)

            line_plot = get_line_plot_for_points_per_play(team_map, pbp_data_with_xp, display_selection)
            st.pyplot(line_plot)
        
        with st.expander("Data Product Type 5: Automated Decision"):

            visitors_performance = LogicService.get_team_performance(team=team_map["Visitors"], side="Visitors", data=pbp_data_with_xp)
            home_performance = LogicService.get_team_performance(team=team_map["Home"], side="Home", data=pbp_data_with_xp)

            # Ergebnisse anzeigen
            col1, col2 = st.columns(2)
            col1.metric(label=f"Performance {team_map['Visitors']}", value=f"{visitors_performance}%", delta=f"{visitors_performance - home_performance}%")
            col2.metric(label=f"Performance {team_map['Home']}", value=f"{home_performance}%", delta=f"{home_performance - visitors_performance}%")

            if scout_team == team_map["Visitors"]:
                if visitors_performance < 100:
                    st.success(f'{team_map["Visitors"]} underperforms with {visitors_performance}% - No Danger.')

                else:
                    st.error(f'{team_map["Visitors"]} overperforms with {visitors_performance}% - Futher Scouting!')

            
            else:
                if visitors_performance < 100:
                    st.success(f'{team_map["Home"]} underperforms with {home_performance}% - No Danger.')

                else:
                    st.error(f'{team_map["Home"]} overperforms with {home_performance}% - Futher Scouting!')



    

# Program
if __name__ == "__main__":
    main()
