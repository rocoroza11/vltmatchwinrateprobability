#67676767

import os 
import pandas as pd

def file_load(game_file):
    if os.path.exists(game_file):
        print(f"The file exists.")
        return True
    else:
        print(f"Error: The file '{game_file}' does not exist.")
        return False
    
def file_write(result):
    try:
        if isinstance(result, pd.DataFrame):
            result.to_csv("pistol_side_conditioned_results.csv", index=False)
            print("File has been saved and stored.")
    except OSError as e:
        print(f"File write failed: {e}")