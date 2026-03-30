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

def load_possession_trees(g: str) -> list[Tree]:
    """Convert play-by-play data into a list of possession trees."""
    df = load_play_by_play(game_id)

    trees = []
    current_path = []
    current_tree = None

    for _, row in df.iterrows():
        event = row.get("EVENTMSGTYPE")
        player1 = row.get("PLAYER1_NAME")
        player2 = row.get("PLAYER2_NAME")

        # --- PASS EVENT ---
        if event == 1 and player1 and player2:  # adjust if needed
            if not current_path:
                current_path = [player1]
                current_tree = Tree(player1)

            current_path.append(player2)

        # --- SHOT EVENT ---
        elif event == 2 and player1:
            if current_tree:
                current_path.append("Shot")
                current_tree.add_path(current_path)
                trees.append(current_tree)

            current_path = []
            current_tree = None

        # --- TURNOVER ---
        elif event == 5 and player1:
            if current_tree:
                current_path.append("Turnover")
                current_tree.add_path(current_path)
                trees.append(current_tree)

            current_path = []
            current_tree = None

        # --- DEFENSIVE REBOUND → NEW POSSESSION ---
        elif event == 4:  # rebound
            current_path = []
            current_tree = None

    return trees
