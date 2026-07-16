#67676767

import os 

def file_load(game_file):
    if os.path.exists(game_file):
        print(f"The file exists.")
        return True
    else:
        print(f"Error: The file '{game_file}' does not exist.")
        return False
    