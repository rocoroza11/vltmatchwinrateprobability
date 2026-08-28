import json
import pandas as pd

def load_rounds_dataframe(json_path="rounds_raw.json"):

    """
    Load round details from a JSON file and return them as a flattened Pandas DataFrame.

    Parameters:
        json_path (str): Path to the input JSON file.

    Returns:
        pd.DataFrame: DataFrame containing parsed round data.
    """

    # Load and parse the raw JSON file
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract team identifiers to use for comparisons
    team_tag = data["team_tag"]
    team_id = data["team_id"]
    rows = []

    # Iterate through nested hierarchy: matches -> maps -> rounds
    for match in data["matches"]:
        for map_data in match["maps"]:
            for r in map_data["rounds"]:

                # Construct base row dictionary with match, map, and round data
                row = {
                    "match_id": match["match_id"],
                    "map_name": map_data["map_name"],
                    **r,  # Merge round details (number, winner_team_short, method, score, etc.)
                }

                # Check if FNC won 
                row["won_by_queried_team"] = (
                    r.get("winner_team_short") == team_tag
                )
                row["fnc_side"] = fnc_side(
                    r, team_id
                )  # Determine side (ATK/DEF) for the target team

                rows.append(row)

    # Convert the list of parsed dictionaries into a DataFrame
    return pd.DataFrame(rows)

def fnc_side(round_, fnc_team_id):

    """
    Determines which side FNC were playing during the round

    Parameters:
        round_: isolated round row in match dataframe
        fnc_team_id: vlr-specific id for Fnatic

    Returns:
        str: "Attacker" or "Defender
    """

    if round_["winner_team_id"] == fnc_team_id:
        return round_["winner_side"]
    else:
        return "Defender" if round_["winner_side"] == "Attacker" else "Attacker"