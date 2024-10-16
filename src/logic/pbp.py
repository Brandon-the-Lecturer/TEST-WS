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
    (data['Time'] > drive_end_time) & \
    (data['EPB'] != data['EPA'])

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

    return df2

def get_pbp_data(season: int, week: int, game: str):
    pbp = DataService_PBP.get_pbp_data(season, week, game)
    
    visitors, home = game.split("-at-")
    drive_visitors = DataService_Drives.get_drive_data(2024, 6, visitors)
    drive_home = DataService_Drives.get_drive_data(2024, 6, home)

    pbp = _add_possession_info(pbp, drive_visitors)
    pbp = _add_possession_info(pbp, drive_home)

    return pbp

def main():
    return


# Program
if __name__ == "__main__":
    main()