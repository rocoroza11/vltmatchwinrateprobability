from beta_dist import analyze_pistol_conversions
from interface import file_write

game_file="rounds_raw.json"
result = analyze_pistol_conversions(game_file)
file_write(result)
