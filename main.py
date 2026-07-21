from pipeline.pandasfile import load_rounds_dataframe
from models.pistol_round2 import pistol_round2_probabilities
from interface import file_write

rounds_df = load_rounds_dataframe()
result = pistol_round2_probabilities(rounds_df)
file_write(result)
