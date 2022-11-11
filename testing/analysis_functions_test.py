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
    totals_db = db_interactions_test()
    # for total in totals:
    #     print(total)
    # print()
    # for total in totals_db:
    #     print(total)
    # print(len(totals))
    # print(len(totals_db))
    # print(af.aggregate_batting_analysis(totals))
    print(af.aggregate_batting_analysis(totals_db))
    stop = timeit.default_timer()
    
    print('Time: ', abs(start-stop))