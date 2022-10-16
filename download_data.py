import codebase.analysis_functions as af
import codebase.web_scrape_functions as wsf
import pandas as pd
import re
from utils import logger
from pprint import pprint

# top_players = wsf.read_statsguru('https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;orderby=batting_average;qualmin1=30;qualval1=matches;template=results;type=batting', table_name='Overall figures')
# top_players = pd.DataFrame(top_players[0])
# top_players.Player = [wsf.player_id_from_link(player, playername=False)[1] for player in top_players.Player]

# players = []
# logger.info("Grabbing all player ids with over 80 innings ot their name")
# for page in range(1,8):
#     logger.info("Processing page %s", page)
#     url = f"https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;orderby=runs;page={page};qualmin1=80;qualval1=innings;template=results;type=batting"
#     players += wsf.read_statsguru(url, table_name='Overall figures')[0].Player.to_list()

# logger.info("Isolating player IDs")
# players = [re.match('/ci/content/player/(\d+)\.html', player[1])[1] for player in players]

error_players = []
for player in ['373696']:
    try:
        logger.info("Grabbing match totals for player %s for the purposes of saving to DB")
        totals = af.get_cricket_totals(int(player), _type='bat', by_innings=True, is_object_id=True, save=True)
        logger.debug(totals)
    except Exception as e:
        logger.error("Error with player %s", player)
        
        logger.exception("Catching literally any error and proceeding so that I can run this overnight, error this time was")
        error_players.append(player)

logger.info("Data collection task completed")
logger.info("Error players are %s", str(error_players))

# result = {}
# for player in top_players.Players:
#     match_list = wsf.player_match_list(player)
#     innings = af.get_cricket_totals(player, match_list, 'bat', True, True, True)
#     innings_df = pd.DataFrame(innings_df)
#     result[player] = af.calculate_running_average(innings_df)

