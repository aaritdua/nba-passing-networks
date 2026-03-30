from nba_api.stats.endpoints import PlayerDashPtPass, CommonTeamRoster, PlayByPlayV3
from nba_api.stats.static import teams, players
import pandas as pd
import time

def load_passing_data(team_id: int, season: str) -> pd.DataFrame:
    """
    Load passing data for all players on a given NBA team for a given season.
    ame_id
    Return a DataFrame where each row represents a passing relationship between two players
    """
    try:
        result = pd.read_csv(f"../data/passing_{team_id}_{season}.csv")
    except:
        roster = CommonTeamRoster(team_id, season).get_data_frames()[0]
        all_data = []
        for player in roster["PLAYER_ID"]:
            df = PlayerDashPtPass(player_id=player, team_id=team_id, season=season).get_data_frames()[0]
            all_data.append(df)
            time.sleep(0.6)
        result = pd.concat(all_data, ignore_index = True)
        result['weight'] = result['PASS'] + result['AST']
        result.to_csv(f"../data/passing_{team_id}_{season}.csv")
    return result


def load_play_by_play(game_id: str) -> pd.DataFrame:
    try:
        result = pd.read_csv(f"../data/playbyplay_{game_id}.csv")
    except:
        result = PlayByPlayV3(game_id=game_id).get_data_frames()[0]
        result.to_csv(f"../data/playbyplay_{game_id}.csv")
    return result
