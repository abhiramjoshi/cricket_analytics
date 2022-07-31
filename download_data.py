import codebase.analysis_functions as af
import codebase.web_scrape_functions as wsf
import pandas as pd

top_players = wsf.read_statsguru('https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;orderby=batting_average;qualmin1=30;qualval1=matches;template=results;type=batting', table_name='Overall figures')
top_players = pd.DataFrame(top_players[0])
top_players.Player = [wsf.player_id_from_link(player, playername=False)[1] for player in top_players.Player]


result = {}
for player in top_players.Players:
    match_list = wsf.player_match_list(player)
    innings = af.get_cricket_totals(player, match_list, 'bat', True, True, True)
    innings_df = pd.DataFrame(innings_df)
    result[player] = af.calculate_running_average(innings_df)

