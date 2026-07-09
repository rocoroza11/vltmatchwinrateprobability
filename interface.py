#67676767

import os 

def file_load(game_file):
    if os.path.exists(game_file):
            with open(game_file, "r", encoding="utf-8") as file:
                content = file.read()
                return content, True
    else:
        print(f"Error: The file '{game_file}' does not exist.")
        return None, False
    