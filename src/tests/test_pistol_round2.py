import pandas as pd

from models.pistol_round2 import pistol_round2_probabilities

def test_pistol_round2_probabilities_are_map_and_side_conditioned():
    rounds_df = pd.DataFrame(
        [
            {
                "match_id": "ascent_atk_1",
                "map_name": "Ascent",
                "number": 1,
                "won_by_queried_team": True,
                "fnc_side": "attack",
            },
            {
                "match_id": "ascent_atk_1",
                "map_name": "Ascent",
                "number": 2,
                "won_by_queried_team": True,
                "fnc_side": "attack",
            },
            {
                "match_id": "ascent_atk_2",
                "map_name": "Ascent",
                "number": 1,
                "won_by_queried_team": True,
                "fnc_side": "attack",
            },
            {
                "match_id": "ascent_atk_2",
                "map_name": "Ascent",
                "number": 2,
                "won_by_queried_team": False,
                "fnc_side": "attack",
            },
            {
                "match_id": "ascent_def_1",
                "map_name": "Ascent",
                "number": 1,
                "won_by_queried_team": True,
                "fnc_side": "defense",
            },
            {
                "match_id": "ascent_def_1",
                "map_name": "Ascent",
                "number": 2,
                "won_by_queried_team": True,
                "fnc_side": "defense",
            },
            {
                "match_id": "haven_atk_1",
                "map_name": "Haven",
                "number": 1,
                "won_by_queried_team": True,
                "fnc_side": "attack",
            },
            {
                "match_id": "haven_atk_1",
                "map_name": "Haven",
                "number": 2,
                "won_by_queried_team": False,
                "fnc_side": "attack",
            },
            {
                "match_id": "haven_atk_2",
                "map_name": "Haven",
                "number": 1,
                "won_by_queried_team": True,
                "fnc_side": "attack",
            },
            {
                "match_id": "haven_atk_2",
                "map_name": "Haven",
                "number": 2,
                "won_by_queried_team": False,
                "fnc_side": "attack",
            },
        ]
    )

    result = pistol_round2_probabilities(rounds_df)

    conditioned = {
        (row.map_name, row.fnc_side): (
            row.n_pistol_wins,
            row.n_win_round2,
            row.p_win_round2_given_pistol,
        )
        for row in result.itertuples()
    }

    assert conditioned == {
        ("Ascent", "attack"): (2, 1, 0.5),
        ("Ascent", "defense"): (1, 1, 1.0),
        ("Haven", "attack"): (2, 0, 0.0),
    }
