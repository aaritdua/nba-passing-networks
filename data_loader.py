"""Functions for loading NBA passing and play-by-play data.

Fetches data from the NBA API and caches results locally as CSV files
to avoid redundant API calls.
"""
import time
import os
from nba_api.stats.endpoints import PlayerDashPtPass, CommonTeamRoster, PlayByPlayV3, leaguegamelog
import pandas as pd


def _get_data_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename)


def load_passing_data(team_id: int, season: str) -> pd.DataFrame:
    """
    Load passing data for all players on a given NBA team for a given season.

    Preconditions:
    - team_id is a valid NBA team ID
    - season is a valid NBA season string in the format 'YYYY-YY'

    Return a pd.DataFrame where each row represents a passing relationship between two players
    """
    try:
        result = pd.read_csv(_get_data_path(f"passing_{team_id}_{season}.csv"))
    except FileNotFoundError:
        roster = CommonTeamRoster(team_id, season).get_data_frames()[0]
        all_data = []
        for player in roster["PLAYER_ID"]:
            df = PlayerDashPtPass(
                player_id=player,
                team_id=team_id,
                season=season
            ).get_data_frames()[0]
            all_data.append(df)
            time.sleep(0.6)
        result = pd.concat(all_data, ignore_index=True)
        result['weight'] = result['PASS'] + result['AST']
        result = result[result['PASS'] >= 10]
        result.to_csv(_get_data_path(f"passing_{team_id}_{season}.csv"))
    return result


def load_play_by_play(game_id: str) -> pd.DataFrame:
    """Load play-by-play data for a game using game_id to identify the play-by-play data

    Preconditions:
    - game_id is a valid NBA game ID

    Return a pd.DataFrame containing the play-by-play data for the game
    """
    try:
        result = pd.read_csv(_get_data_path(f"playbyplay_{game_id}.csv"))
    except FileNotFoundError:
        result = PlayByPlayV3(game_id=game_id).get_data_frames()[0]
        result.to_csv(_get_data_path(f"playbyplay_{game_id}.csv"))
    return result


def load_game_ids(team_id: int, season: str) -> list[str]:
    """Return a list of game IDs for a given team and season.

    Preconditions:
        - team_id is a valid NBA team ID
        - season is a valid NBA season string in the format 'YYYY-YY'
    """
    cache_path = _get_data_path(f"games_{team_id}_{season}.csv")
    try:
        result = pd.read_csv(cache_path)
        return result['GAME_ID'].tolist()
    except FileNotFoundError:
        games = leaguegamelog.LeagueGameLog(season=season).get_data_frames()[0]
        games = games[games['TEAM_ID'] == team_id]
        games.to_csv(cache_path)
        return games['GAME_ID'].tolist()
