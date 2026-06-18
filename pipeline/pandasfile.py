import json 
import pandas as pd 

with open("matches.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data["matches"])

df[["team1_score", "team2_score"]] = df["score"].str.split("-", expand=True).astype(int)

df["result"] = df.apply(
    lambda row: "W" if row["team1_score"] > row["team2_score"] else "L",
    axis=1
)

df["score_diff"] = df["team1_score"] - df["team2_score"]

df["result"].value_counts() 

print(df)

