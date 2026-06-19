from pipeline.pandasfile import load_rounds_dataframe
from models.pistol_round2 import pistol_round2_probabilities

rounds_df = load_rounds_dataframe("rounds_raw.json")
result = pistol_round2_probabilities(rounds_df)
print(result)