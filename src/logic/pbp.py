import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import numpy as np
import pandas as pd

import data.drives as DataService_Drives
import data.pbp as DataService_PBP


# Const.

# Func

def __add_possession_info_per_drive(
        pbp: pd.DataFrame, 
        drive_quarter:int, 
        drive_start_time:pd.Timedelta, 
        drive_end_time:pd.Timedelta, 
        team:str) -> pd.DataFrame:
    
    mask = (pbp['Quarter'] == drive_quarter) & \
    (pbp['Time'] <= drive_start_time) & \
    (pbp['Time'] > drive_end_time)

    pbp.loc[mask, "Possession"] = team
    return pbp

def __add_possession_info(pbp: pd.DataFrame, drive:pd.DataFrame ) -> pd.DataFrame:

    for _, drive_row in drive.iterrows():

        drive_possession_team = drive_row["Team"]
        drive_start_time = drive_row['Time']
        drive_end_time = drive_row['Time'] - drive_row['Length']
        drive_quarter = drive_row['Quarter']
        
        if drive_end_time >= pd.Timedelta(0):
            pbp = __add_possession_info_per_drive(pbp, drive_quarter, drive_start_time, drive_end_time, drive_possession_team)
            
        else:
            pbp = __add_possession_info_per_drive(pbp, drive_quarter, drive_start_time, pd.Timedelta(0), drive_possession_team)

            pbp = __add_possession_info_per_drive(pbp, drive_quarter+1, pd.Timedelta(minutes=15), drive_end_time+pd.Timedelta(15), drive_possession_team)

    pbp.loc[(pbp['EPB'] == 0) & (pbp['EPA'] == 0), 'Possession'] = pbp['Possession'].shift()
    return pbp

def __add_drive_counter(data:pd.DataFrame) -> pd.DataFrame:
    data['Drive_No'] = (data['Possession'] != data['Possession'].shift()).cumsum()
    data['Drive_No'] = data['Drive_No'].astype('int')
    return data

def __fill_with_max_until_max_reached(group):
    max_value = group['EPB'].max()
    max_index = group['EPB'].idxmax()
    
    # Werte bis zum Maximum kopieren, danach mit dem Maximalwert auffüllen
    group['xP'] = group['EPB'].where(group.index <= max_index, max_value)
    
    # Negative Werte in xP durch 0 ersetzen
    group['xP'] = group['xP'].clip(lower=0)
    
    # Sicherstellen, dass xP stetig steigend ist
    group['xP'] = group['xP'].cummax()
    
    return group

def __accumulate_max_to_next_group(group):
    # Nach Drive_No gruppieren
    drives = group.groupby('Drive_No')
    new_column = group['xP'].copy()  # Kopie der EPB-Spalte für die Berechnungen
    accumulated_max = 0  # Initialisierungswert für den kumulierten Maximalwert

    # Iteriere über die Drives und aktualisiere die Werte der nächsten Gruppe
    for drive_no, sub_group in drives:
        # Berechne den Maximalwert der aktuellen Gruppe
        current_max = sub_group['xP'].max()
        
        # Aktualisiere die EPB-Werte in der aktuellen Gruppe um den akkumulierten Maximalwert
        new_column.loc[sub_group.index] += accumulated_max
        
        # Setze den akkumulierten Maximalwert für die nächste Gruppe
        accumulated_max += current_max

    # Füge die neue Spalte dem DataFrame hinzu
    group['xP_cum'] = new_column
    return group


def get_pbp_data(season: int, week: int, game: str) -> pd.DataFrame:
    return DataService_PBP.get_pbp_data(season, week, game)

def get_pbp_data_agg(season: int, week: int, game: str):
    pbp = DataService_PBP.get_pbp_data(season, week, game)
    
    visitors, home = game.split("-at-")
    drive_visitors = DataService_Drives.get_drive_data(season, week, visitors)
    drive_home = DataService_Drives.get_drive_data(season, week, home)

    pbp = __add_possession_info(pbp, drive_visitors)
    pbp = __add_possession_info(pbp, drive_home)
    pbp = __add_drive_counter(pbp)
    return pbp

def get_pbp_data_with_xp(season: int, week: int, game: str):
    pbp = get_pbp_data_agg(season, week, game)

    pbp = pbp.groupby('Drive_No', group_keys=False).apply(__fill_with_max_until_max_reached)
    pbp = pbp.groupby('Possession', group_keys=False).apply(__accumulate_max_to_next_group)
    return pbp

def __get_team_performance(team:str, data: pd.DataFrame, side: str):
    team_data = data[data['Possession'] == team]

    potential_performance = np.trapz(team_data['xP_cum'], x=team_data.index)
    actual_performance = np.trapz(team_data[side], x=team_data.index)

    relative_performance = int((actual_performance / potential_performance) *100)

    return relative_performance

def get_performances(season: int, week: int, visitors:str, home: str) -> tuple:
    data = get_pbp_data_with_xp(season, week, f"{visitors}-at-{home}")
    visitors_performance = __get_team_performance(visitors, data, "Visitors")
    home_performance = __get_team_performance(home, data, "Home")
    return (visitors_performance, home_performance) 

def main():
    return


# Program
if __name__ == "__main__":
    main()