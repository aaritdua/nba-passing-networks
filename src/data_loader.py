"""CSC111 Winter 2026 Project 2: Mapping the Flow

Created by: Aarit Dua, Vedant Kansara, Lucas Hui

Title: data_loader
Description: This file contains functions for loading NBA passing and play-by-play data,
either from locally saved CSV files (from the NBA API) or by retrieving it from the NBA API.

Copyright and Usage Information
===============================

This file is provided for educational and personal use only. You may view, download, and modify the code for your own
non-commercial purposes, provided that proper credit is given to the original author.
You may not redistribute, publish, or use this project or any modified version of it for commercial purposes without
explicit written permission from the author.
This project may include third-party libraries, data, or tools that are subject to their own licenses and terms of use.
Users are responsible for reviewing and complying with those licenses.
"""
import time
from nba_api.stats.endpoints import PlayerDashPtPass, CommonTeamRoster, PlayByPlayV3
import pandas as pd


def load_passing_data(team_id: int, season: str) -> pd.DataFrame:
    """
    Load passing data for all players on a given NBA team for a given season.
    ame_id

    Preconditions:
    - team_id is a valid NBA team ID
    - season is a valid NBA season string in the format 'YYYY-YY'

    Return a pd.DataFrame where each row represents a passing relationship between two players
    """
    try:
        result = pd.read_csv(f"../data/passing_{team_id}_{season}.csv")
    except FileNotFoundError:
        roster = CommonTeamRoster(team_id, season).get_data_frames()[0]
        all_data = []
        for player in roster["PLAYER_ID"]:
            df = PlayerDashPtPass(player_id=player, team_id=team_id, season=season).get_data_frames()[0]
            all_data.append(df)
            time.sleep(0.6)
        result = pd.concat(all_data, ignore_index=True)
        result['weight'] = result['PASS'] + result['AST']
        result.to_csv(f"../data/passing_{team_id}_{season}.csv")
    return result


def load_play_by_play(game_id: str) -> pd.DataFrame:
    """Load play-by-play data for a game using game_id to identify the play-by-play data

    Preconditions:
    - game_id is a valid NBA game ID

    Return a pd.DataFrame containing the play-by-play data for the game
    """
    try:
        result = pd.read_csv(f"../data/playbyplay_{game_id}.csv")
    except FileNotFoundError:
        result = PlayByPlayV3(game_id=game_id).get_data_frames()[0]
        result.to_csv(f"../data/playbyplay_{game_id}.csv")
    return result


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['csv', 'networkx'],
        'allowed-io': ['load_review_graph'],
        'max-nested-blocks': 4
    })
