import os
import sys
import timeit
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f'Base: {BASE_PATH}')
sys.path.append(BASE_PATH)
from espncricinfo.match import Match
from codebase.match_data import MatchData
from pprint import pprint
import codebase.analysis_functions as af
import codebase.web_scrape_functions as wsf
import re
import json

TEST_MATCH_ID = 668951
M = MatchData(TEST_MATCH_ID)
PLAYER_ID = 373696

def test_aggregate_fetch(m):
    return af.get_aggregates(m, 'bat-fours')

def test_player_contributions(m, is_object_id=False, by_innings=False):
    print('Both\n------')
    pprint(af._get_player_contribution(PLAYER_ID, m, is_object_id=is_object_id, by_innings=by_innings))
    print('Bat\n------')
    pprint(af._get_player_contribution(PLAYER_ID, m, 'bat', is_object_id=is_object_id, by_innings=by_innings))
    print('Bowl\n------')
    pprint(af._get_player_contribution(PLAYER_ID, m, 'bowl', is_object_id=is_object_id, by_innings=by_innings))

def test_cricket_totals(player_id, m, is_object_id=False, by_innings=False):
    totals = af._cricket_totals(player_id, m, is_object_id=is_object_id, by_innings=by_innings)
    print('Batting\n------')
    print(totals['bat'])
    print()
    print('Bowling\n------')
    print(totals['bowl'])
    print()

def test_get_career_batting_graph(player_id, dates=None, _format='test', window_size=12):
    af.get_career_batting_graph(player_id, dates=dates, _format=_format, window_size=window_size)

def test_running_average(player_id, _format='test'):
    running_average = af.get_running_average(player_id)

def test_get_figures_from_scorecard(player_id, match, _type, is_object_id):
    figures = af.get_figures_from_scorecard(player_id, match, _type, is_object_id)
    return figures

def test_runout_while_nonstriker(commentary_df, player_id, match_object, is_object_id = False):
    return af.check_runout_while_nonstriker(commentary_df=commentary_df, player_id=player_id, match_object=match_object, is_object_id=is_object_id)

def db_interactions_test():
    return af.get_cricket_totals(PLAYER_ID, _type='bat', by_innings=True, is_object_id=True, try_local=True)

if __name__ == '__main__':
    start = timeit.default_timer()
    #commentary_df = af.pre_transform_comms(M)
    # print(test_aggregate_fetch(M))
    # test_player_contributions(M, is_object_id=True, by_innings=True)
    # test_cricket_totals(PLAYER_ID, M, is_object_id=True, by_innings=True)
    # print(test_runout_while_nonstriker(commentary_df, PLAYER_ID, M, True))
    # print(af.get_player_contributions(PLAYER_ID, TEST_MATCH_ID, _type='bat', by_innings= True, is_object_id= True))
    # af.apply_aggregate_func_to_list(['253802', '303669', '277906', '267192'], [af.get_recent_form_average, af.get_running_average], dates='2020-02-21:', disable_logging=False)
    # print(test_runout_while_nonstriker(commentary_df, PLAYER_ID, M, True))
    # test_running_average(PLAYER_ID)
    # test_get_career_batting_graph(PLAYER_ID, dates='2020-01-01:')
    # print(test_get_figures_from_scorecard(PLAYER_ID, M, 'bat', True))
    # totals = af.get_cricket_totals(253802, _type='bat', by_innings=True, is_object_id=True, try_local=False, from_scorecards=True)
    #IAN_BELL = 9062
    #totals = af.get_cricket_totals(IAN_BELL, _type='bat', by_innings=True, is_object_id=True, try_local=False)
    totals = af.get_cricket_totals(326434, _type='bat', by_innings=True, is_object_id=True, try_local=True)
    period_stats = af.get_player_performances_in_periods(int(326434), 80, cricket_totals=totals, cricket_runs_ave=True)
    best_period = af.get_best_periods(326434, periodic_stats=period_stats)
    #totals_db = db_interactions_test()
    # for total in totals:
    #     print(total)
    # print()
    # for total in totals_db:
    #     print(total)
    # print(len(totals))
    # print(len(totals_db))
    # print(af.aggregate_batting_analysis(totals))
    # print(af.aggregate_batting_analysis(totals_db))
    #print(best_period)
    #print(totals[25:105])

    # players_grabbed = []
    # #logger.info("Grabbing all player ids with over 80 innings ot their name")
    # for page in range(1,8):
    # #    logger.info("Processing page %s", page)
    #     url = f"https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;orderby=runs;page={page};qualmin1=80;qualval1=innings;template=results;type=batting"
    #     players_grabbed += wsf.read_statsguru(url, table_name='Overall figures')[0].Player.to_list()

    # #logger.info("Isolating player IDs")
    # players = [re.match('/ci/content/player/(\d+)\.html', player[1])[1] for player in players_grabbed]
    # print(players[100:101])
    # best_80 = {}
    # for player in players:
    #     cricket_totals = af.get_cricket_totals(int(player), _type='bat', by_innings=True, try_local=True, is_object_id=True)
    #     period_stats = af.get_player_performances_in_periods(int(player), 80, cricket_totals=cricket_totals, cricket_runs_ave=True)
    #     #pprint([period_stats[80][period]['averages']['runs'] for period in period_stats[80]])
    #     best_period = af.get_best_periods(player, periodic_stats=period_stats)
    #     best_80[player] = best_period

    # with open('best_80_cricket_average.json', 'w') as f:
    #     json.dump(best_80, f)

    stop = timeit.default_timer()
    
    print('Time: ', abs(start-stop))