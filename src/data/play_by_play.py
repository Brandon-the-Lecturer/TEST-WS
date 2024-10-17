# Dependencies
import pandas as pd
import os


# Variables
FILE_DIR_PATH = '/workspaces/TEST-WS/src/data/pbp'
DTYPES_PBP = {
    'Quarter': int,
    'Time': 'timedelta64[ns]',
    'Down': int,
    'ToGo': int,
    'Location': str,
    'Visitors': int,
    'Home': int,
    'Detail': str,
    'EPB': float,
    'EPA': float
}

# Functions
def _get_pbp_file_names(path: str = FILE_DIR_PATH) -> list:
    pbp_file_names = os.listdir(path)
    return [os.path.splitext(datei)[0] for datei in pbp_file_names]

def get_seasons(file_names:list = _get_pbp_file_names()):
    return list(set([int(file_name.split("-")[0]) for file_name in file_names]))

def get_week_of_season(season: int, file_names:list = _get_pbp_file_names()):
    return list(set([int(file_name.split("-")[1]) for file_name in file_names if int(file_name.split("-")[0]) == season ]))

def get_game_of_week(week:int, season: int, file_names:list = _get_pbp_file_names()):
    return list([file_name.split("-", 2)[2] for file_name in file_names if (int(file_name.split("-")[0]) == season) and (int(file_name.split("-")[1])) == week ])

def _get_game_file(season: int, week: int, game: str) -> str:
    game_files = os.listdir(FILE_DIR_PATH)

    game_file_path = [file for file in game_files 
                if file.endswith('.csv') 
                and str(season) in file 
                and str(week).zfill(2) in file 
                and game in file][0]
    return game_file_path

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

def _standardize_columns(data:pd.DataFrame, columns: list) -> pd.DataFrame:
    copy_df = data.copy()
    copy_df.columns = columns
    return copy_df

def get_pbp_data(season:int, week: int, game: str) -> pd.DataFrame:
    game_file = _get_game_file(season, week, game)
    
    # Read Data
    pbp_data = pd.read_csv(FILE_DIR_PATH+"/"+game_file)

    # Clean Data
    pbp_data = _clean_dataset(pbp_data)
    pbp_data = _standardize_columns(pbp_data, DTYPES_PBP.keys())
    pbp_data = _change_dtypes(pbp_data, DTYPES_PBP)
    pbp_data["Home"] = pbp_data["Home"].cummax()
    pbp_data["Visitors"] = pbp_data["Visitors"].cummax()

    return pbp_data

def main():
    print("Filenames")
    print(_get_pbp_file_names())
    
    print("Seasons")
    print(get_seasons())
    
    print("Week")
    print(get_week_of_season(season=2024))
    
    print("Game")
    print(get_game_of_week(week=6, season=2024))
    
    print("Game File Path")
    print(_get_game_file(game="was-at-bal", week=6, season=2024))
    
    print("PBP Data")
    pbp_data = get_pbp_data(game="was-at-bal", week=6, season=2024)
    print(pbp_data.head())
    
    return 

# Program
if __name__ == "__main__":
    main()