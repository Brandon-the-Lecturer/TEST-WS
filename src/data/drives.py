# Dependencies
import pandas as pd
import os


# Variables
# Aktuelles Verzeichnis, in dem das Skript läuft


# Zielordner auf derselben Ebene wie das Skript
DATA_DIR_NAME  = 'drives'
DTYPES_DRIVE = {
    '#': int,
    'Quarter': int,
    'Time': 'timedelta64[ns]',
    'LOS': str,
    'Plays': int,
    'Length': 'timedelta64[ns]',
    'Net Yds': int,
    'Result': str,
}

# Functions

def _get_data_dir_path():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(current_directory, DATA_DIR_NAME)
    return data_directory

def _get_game_file(season: int, week: int, team: str) -> str:
    data_directory = _get_data_dir_path()
    game_files = os.listdir(data_directory)
    
    # Finde alle passenden Dateien
    matching_files = [
        file for file in game_files
        if file.endswith('.csv')
        and str(season) in file
        and str(week).zfill(2) in file
        and team in file
    ]
    
    # Gebe den ersten Treffer zurück oder None, falls die Liste leer ist
    return matching_files[0] if matching_files else None

def _convert_to_timedelta(df, column_name):
    df[column_name] = df[column_name].astype(str)
    df[column_name] = pd.to_timedelta('00:' + df[column_name])
    return df

def _change_dtypes(df, dtype_dict):
    for column, dtype in dtype_dict.items():
        if dtype == 'timedelta64[ns]':
            df = _convert_to_timedelta(df, column)
        else:
            df[column] = df[column].astype(dtype)
    
    return df

def _clean_dataset(data: pd.DataFrame) -> pd.DataFrame:
    copy_df = data.copy()
    copy_df.dropna(subset=["Time"], inplace=True)
    copy_df.fillna(0, inplace=True)
    return copy_df

def _add_team_info(data: pd.DataFrame, team: str) -> pd.DataFrame:
    copy_df = data.copy()
    copy_df["Team"] = team
    return copy_df

def check_for_data(season: int, week: int, team: str) -> bool:
    return (_get_game_file(season, week, team) is not None)

def get_drive_data(season:int, week: int, team: str) -> pd.DataFrame:
    game_file = _get_game_file(season, week, team)
    
    # Read Data
    data_directory = _get_data_dir_path()
    drive_data = pd.read_csv(data_directory+"/"+game_file)

    # Clean Data
    drive_data = _clean_dataset(drive_data)
    drive_data = _change_dtypes(drive_data, DTYPES_DRIVE)
    drive_data = _add_team_info(drive_data, team)

    return drive_data

def main():
    print(check_for_data(
        season=2024, 
        week=6, 
        team='bal'))
    
    drive_data = get_drive_data(
        season=2024, 
        week=6, 
        team='bal')
    
    print(drive_data.info())
    print(drive_data.head())
    return 


# Program
if __name__ == "__main__":
    main()