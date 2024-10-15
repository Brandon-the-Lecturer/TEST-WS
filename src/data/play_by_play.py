# Dependencies
import pandas as pd
import os


# Variables
FILE_DIR_PATH = '/workspaces/TEST-WS/src/data/pbp'

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

def get_pbp_data(season:int, week: int, game: str) -> pd.DataFrame:
    game_file = _get_game_file(season, week, game)
    return pd.read_csv(FILE_DIR_PATH+"/"+game_file)

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
    print(get_pbp_data(game="was-at-bal", week=6, season=2024).head())

    return 

# Program
if __name__ == "__main__":
    main()