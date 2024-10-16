import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import pandas as pd

import data.drives as DataService_Drives
import data.play_by_play as DataService_PBP


# Const.

# Func

def _add_possession_info_per_drive(
        data: pd.DataFrame, 
        drive_quarter:int, 
        drive_start_time:pd.Timedelta, 
        drive_end_time:pd.Timedelta, 
        team:str) -> pd.DataFrame:
    
    mask = (data['Quarter'] == drive_quarter) & \
    (data['Time'] <= drive_start_time) & \
    (data['Time'] > drive_end_time)

    data.loc[mask, "Possession"] = team
    return data

def _add_possession_info(df2: pd.DataFrame, df1:pd.DataFrame ) -> pd.DataFrame:

    for _, drive_row in df1.iterrows():

        drive_possession_team = drive_row["Team"]
        drive_start_time = drive_row['Time']
        drive_end_time = drive_row['Time'] - drive_row['Length']
        drive_quarter = drive_row['Quarter']
        
        if drive_end_time >= pd.Timedelta(0):
            df2 = _add_possession_info_per_drive(df2, drive_quarter, drive_start_time, drive_end_time, drive_possession_team)
            
        else:
            df2 = _add_possession_info_per_drive(df2, drive_quarter, drive_start_time, pd.Timedelta(0), drive_possession_team)

            df2 = _add_possession_info_per_drive(df2, drive_quarter+1, pd.Timedelta(minutes=15), drive_end_time+pd.Timedelta(15), drive_possession_team)

    df2.loc[(df2['EPB'] == 0) & (df2['EPA'] == 0), 'Possession'] = df2['Possession'].shift()
    return df2


def _add_drive_counter(data:pd.DataFrame) -> pd.DataFrame:
    data['Drive_No'] = (data['Possession'] != data['Possession'].shift()).cumsum()
    data['Drive_No'] = data['Drive_No'].astype('int')
    return data

def _fill_with_max_until_max_reached(group):
    max_value = group['EPB'].max()
    max_index = group['EPB'].idxmax()
    # Werte bis zum Maximum kopieren, danach mit dem Maximalwert auffüllen
    group['xP'] = group['EPB'].where(group.index <= max_index, max_value)
    return group

def get_pbp_data(season: int, week: int, game: str):
    pbp = DataService_PBP.get_pbp_data(season, week, game)
    
    visitors, home = game.split("-at-")
    drive_visitors = DataService_Drives.get_drive_data(2024, 6, visitors)
    drive_home = DataService_Drives.get_drive_data(2024, 6, home)

    pbp = _add_possession_info(pbp, drive_visitors)
    pbp = _add_possession_info(pbp, drive_home)
    pbp = _add_drive_counter(pbp)
    return pbp

def get_pbp_data_with_xp(season: int, week: int, game: str):
    pbp = get_pbp_data(season, week, game)
    return pbp.groupby('Drive_No', group_keys=False).apply(_fill_with_max_until_max_reached)

def main():
    return


# Program
if __name__ == "__main__":
    main()