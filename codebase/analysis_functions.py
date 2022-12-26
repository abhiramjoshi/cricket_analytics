from collections import defaultdict
import codebase.match_data as match
import codebase.web_scrape_functions as wsf
import numpy as np
import pandas as pd
import sklearn.utils
import matplotlib.pyplot as plt
import seaborn as sns
import re
import string
import utils
from utils import FiguresInDB, logger
from collections.abc import Iterable
from datetime import datetime
import espncricinfo.exceptions as cricketerrors
import warnings
from math import isnan
from sqlalchemy.orm import sessionmaker
from models import engine, PlayerMatchStats, Match

NULL_BATTING_ANALYSIS = {
    'runs': 0,
    'dismissals': 0,
    'balls_faced': 0,
    'sr': 0,
    'average': 0,
    'dot_balls': 0,
    'ones': 0, 
    'twos': 0,
    'threes': 0, 
    'fours': 0,
    'fives': 0,
    'sixes': 0,
    'how-out': None,
    'not-out':None,
    'total_balls_faced': 0,
    'fours_per_ball': 0,
    'sixes_per_ball': 0,
    'dots_per_ball': 0
}

def pre_transform_comms(match_object:match.MatchData):
    logger.info(f'Pre-transforming match commentary for {match_object.match_id}')
    df = pd.DataFrame.from_dict(match_object.get_full_comms())
    if df.empty:
        raise utils.NoMatchCommentaryError
    logger.debug(f"Columns of commentary from match {match_object.match_id}")
    logger.debug(f'Columns: {df.columns}\nSize: {df.size}')
    map_players(match_object, df)
    logger.info(f'{match_object.match_id}: Processing text commentary fields')
    process_text_comms(df)
    logger.info(f'{match_object.match_id}: Processing bowler runs')
    df['bowlerRuns'] = df['batsmanRuns'] + df['wides'] + df['noballs']
    try:
        innings_map = {int(inning['innings_number']): int(inning['team_id']) for inning in match_object.innings_list}
    except KeyError:
        innings_map = {int(inning['innings_number']): int(inning['batting_team_id']) for inning in match_object.innings}
    df['battingTeam'] = df['inningNumber'].map(innings_map)
    df['dismissedBatsman'] = df['batsmanPlayerId']
    df.loc[df['isWicket'] == False, 'dismissedBatsman'] = None
    return df

def how_out(dismissal_code, keep_code = False):
    DISMISSAL_DICT = {
        1: 'caught',
        2: 'bowled',
        3: 'lbw',
        4: 'run_out',
        5: 'stumped',
        6: 'hit_wicket',
        13: False
    }
    if keep_code:
        return dismissal_code
    try:
        return DISMISSAL_DICT[dismissal_code]
    except:
        logger.info('Dismissal code was %s', dismissal_code)
        return False

def dates_from_age(player_id, age_range):
    if age_range:
        player_dob = get_player_dob(player_id)
        try:
            player_age = age_range.split(':')
            younger_bound = player_age[0]
            if not bool(younger_bound):
                younger_bound = player_dob
            else:
                younger_bound = int(younger_bound)
                younger_bound = player_dob.replace(year=player_dob.year+int(younger_bound)).strftime('%Y-%m-%d')
            try:
                older_bound = player_age[1]
                if not bool(older_bound):
                    older_bound = datetime.now()
                else:
                    older_bound = int(older_bound)
                    older_bound = player_dob.replace(year=player_dob.year+int(older_bound)).strftime('%Y-%m-%d')
            except IndexError:
                older_bound = int(younger_bound)+1
                older_bound = player_dob.replace(year=player_dob.year+int(older_bound)).strftime('%Y-%m-%d')
        except ValueError:
            logger.error('Invalid value for player age')
        
        return f"{younger_bound}:{older_bound}"
    return None

def get_balls_event(comms:pd.DataFrame, column_name:str, value, negative=False):
    if negative:
        event_df = comms[comms[column_name] != value]    
    else:
        event_df = comms[comms[column_name] == value]
    return event_df

def get_player_dob(player_id):
    json = wsf.get_player_json(player_id)
    age = datetime.strptime(json['dateOfBirth'], '%Y-%m-%dT%H:%MZ')
    return age

def get_player_map(match_object:match.MatchData, map_to:str='card_long',map_from='player_id'):
    return {int(player[map_from]):player[map_to] for player in match_object.all_players}

def map_players(match_object:match.MatchData, comms:pd.DataFrame):
    logger.debug(f'{match_object.match_id}: Mapping player names')
    player_map = get_player_map(match_object)
    comms["batsmanName"] = comms["batsmanPlayerId"].map(player_map)
    comms["bowlerName"] = comms["bowlerPlayerId"].map(player_map)

def series_to_df(series:pd.Series, column_names:list, remove_index:bool=True):
    if isinstance(series, pd.Series):
        df = series.to_frame()
    else:
        df = series
    df.rename(columns={df.columns[0]: column_names[1]}, inplace=True)
    if remove_index:
        df[column_names[0]] = df.index
        df.reset_index(drop=True, inplace=True)
    columns = df.columns.tolist()
    df = df[[columns[1], columns[0]]]
    return df
    
def graph_seaborn_barplot(data, x, y, hue=None):
    sns.set_theme()
    fig_dims = (15,10)
    fig,ax = plt.subplots(figsize=fig_dims)
    bar = sns.barplot(data=data, x=x, y=y, ax=ax, hue=hue);
    bar.set_xticklabels(bar.get_xticklabels(), rotation=90);
    plt.setp(ax.patches, linewidth=0)

def check_player_in_match(player_id, _match:match.MatchData, is_object_id=False):
    if is_object_id:
        player_id = get_player_map(_match, 'player_id', 'object_id')[player_id]
    
    logger.info('Checking if player %s is part of match %s', player_id, _match.match_id)
    players = [int(player['player_id']) for player in _match.all_players]
    if int(player_id) not in players:
        logger.warning('Player not part of match')
        raise utils.PlayerNotPartOfMatch
    logger.info("Player in match")

def get_player_team(player_id, _match:match.MatchData, is_object_id=False):
    """
    Returns a dict indicating the given players team and the opposition
    return {'team': _match.team_1_id, 'opposition': _match.team_2_id}
    """
    
    if is_object_id:
        map_id = 'object_id'
    else:
        map_id = 'player_id'

    team_1 = [int(player[map_id]) for player in _match.team_1_players]
    team_2 = [int(player[map_id]) for player in _match.team_2_players]
    
    if int(player_id) in team_1:
        return {'team': _match.team_1_id, 'opposition': _match.team_2_id}
    elif int(player_id) in team_2:
        return {'team': _match.team_2_id, 'opposition': _match.team_1_id}
    else:
        raise utils.PlayerNotPartOfMatch('Player not part of match')

def get_aggregates(match_object: match.MatchData, event):
    events = {
        'bat-runs':('batsmanRuns', 'batsman', 2),
        'bowl-runs':('bowlerRuns', 'bowler', 2),
        'wickets':('isWicket', 'bowler', 1),
        'bat-fours': ('isFour', 'batsman', 1),
        'bowl-fours': ('isFour', 'bowler', 1),
        'bat-sixes':('isSix', 'batsman', 1),
        'bowl-sixes':('isSix', 'bowler', 1),
        'byes':('byes', None, 3),
        'legbyes':('legbyes', None, 3)
    }
    event_mapped = events[event]
    comms = pre_transform_comms(match_object)
    if event_mapped[2] == 1:
        event_s = get_balls_event(comms, column_name=event_mapped[0], value=True)
        event_df = series_to_df(event_s[f'{event_mapped[1]}Name'].value_counts(), [event_mapped[1], event])
    if event_mapped[2] == 2:
        event_df = comms[[f'{event_mapped[1]}Name', event_mapped[0]]]
        event_df = event_df.groupby(f'{event_mapped[1]}Name').sum().sort_values(by=event_mapped[0])
        event_df = series_to_df(event_df, [event_mapped[1], event])
    graph_seaborn_barplot(event_df, event_df.columns[0],event_df.columns[1])

    return event_df

def get_match_details_from_db(_match:match.MatchData or int):
    if isinstance(_match, match.MatchData):
        _match = _match.match_id

    Session = sessionmaker(bind=engine)
    with Session() as session:
        _match = session.query(Match).filter_by(match_id=_match).all()
    if _match:
        _match = utils.object_as_dict(_match[0])

        _match_dict = {
            'date':_match['date'],
            'teams':[_match['team_1_players'], _match['team_2_players']],
            'team_1':_match['team_1'],
            'team_2':_match['team_2'],
            'continent':_match['continent'],
            'ground':_match['ground'],
            'result':_match['result'],
            'total_innings':_match['total_innings']
        }

        return _match_dict

def get_figures_from_db(player_id, _match:match.MatchData or int, _type, is_object_id = False):
    """Get figures from DB, player id must not be object id"""
    if isinstance(_match, match.MatchData):
        _match = _match.match_id
    
    if is_object_id:
        PLAYER_SEARCH = {'player_object_id':player_id}
    else:    
        PLAYER_SEARCH = {'player_id':player_id}

    Session = sessionmaker(bind=engine)
    with Session() as session:
        figures = session.query(PlayerMatchStats).filter_by(**PLAYER_SEARCH).filter_by(match_id=_match).all()

    if _type == 'bat':
        batting_figures = []
        for row in figures:
            row = utils.object_as_dict(row)
            row_dict = {
                'inning': row['inning'],
                'runs': row['bat_runs'],
                'balls_faced': row['balls_faced'],
                'fours': row['bat_fours'],
                'six': row['bat_sixes'],
                'dot_balls': row['bat_dot_balls'],
                'not_out': row['not_out'],
                'how_out': row['how_out']   
            }
            batting_figures.append(row_dict)
        return batting_figures 
        
    if _type == 'bowl':
        bowling_figures = []
        for row in figures:
            row = utils.object_as_dict(row)
            row_dict = {
                'inning':row['inning'],
                'overs': row['bowl_overs'],
                'runs': row['bowl_runs'],
                'dot_balls': row['bowl_dot_balls'],
                'wides': row['bowl_wides'],
                'noballs': row['bowl_noballs'],
                'wickets': row['wickets']
            }
            bowling_figures.append(row_dict)
        return bowling_figures

def get_figures_from_scorecard(player_id, _match:match.MatchData, _type, is_object_id=False):
    if not is_object_id: #Change to object ID
        player_id = get_player_map(_match, 'object_id', 'player_id')[player_id]
    url = _match.match_url
    scorecard = wsf.get_match_scorecard(url, match_id=_match.match_id)

    def int_or_none(value):
        try:
            return int(value)
        except ValueError:
            return None

    if _type == 'bowl':
        all_bowlers = [(bowler,innings) for innings in scorecard for bowler in scorecard[innings]['bowling']]
        
        figures = [f for f in all_bowlers if int(f[0]['bowler'][1]) == int(player_id)]
        bowling_figures = []
        for inning_figures, innings in figures:
            inning_bowling_figures = {
                    'inning': int_or_none(inning),
                    'overs': inning_figures['O'],
                    'runs': int_or_none(inning_figures['R']),
                    'dot_balls': 0,
                    'wides': int_or_none(inning_figures['WD']),
                    'noballs': int_or_none(inning_figures['NB'])
                    #need to add wickets, maidens, 4s, 6s, econ
                }
            bowling_figures.append(inning_bowling_figures)
        return bowling_figures
    if _type == 'bat':
        all_batsman = [(batsman,innings) for innings in scorecard for batsman in scorecard[innings]['batting']]
        figures = [f for f in all_batsman if int(f[0]['batsman'][1]) == int(player_id)]
        batting_figures = []
        for inning_figures,inning in figures:
            inning_batting_figures = {
                    'inning': int_or_none(inning.strip('inning_')),
                    'runs': int_or_none(inning_figures['R']),
                    'balls_faced': int_or_none(inning_figures['B']),
                    'fours': int_or_none(inning_figures['4s']),
                    'six': int_or_none(inning_figures['6s']),
                    'dot_balls': 0,
                    'not_out': not bool(inning_figures['out']),
                    'how_out': inning_figures['out']
                }
            batting_figures.append(inning_batting_figures)
        return batting_figures

def stat_db_record_exists(player_id, match_id, stats, stat_id = None):
    """
    Searches db to see if stat exists.
    Player ID **is not** object_id
    """
    Session = sessionmaker(bind=engine)
    with Session() as session:
        if not stat_id:
            stat_id = f"{player_id}{match_id}{stats['inning']}"
        stat = session.query(PlayerMatchStats).filter_by(stat_id=stat_id).all()
        if stat:
            return True
        else:
            return False

def save_player_stats_to_db(stats, player_id, _match:match.MatchData, is_object_id=True, force=False):

    match_id = _match
    if isinstance(_match, match.MatchData):
        match_id = _match.match_id

    logger.info("Saving player stats to DB")

    KEY_MAP_BAT = {
        'runs':'bat_runs',
        'fours':'bat_fours',
        'six':'bat_sixes',
        'dot_balls':'bat_dot_balls',
    }
    
    KEY_MAP_BOWL = {
        'runs':'bowl_runs',
        'overs':'bowl_overs',
        'dot_balls':'bowl_dot_balls',
        'wides':'bowl_wides',
        'noballs':'bowl_noballs'
    }

    _type = stats.pop('type')

    if _type == 'bat':
        mapping = KEY_MAP_BAT
    if _type == 'bowl':
        mapping = KEY_MAP_BOWL

    stats_c = stats.copy()
    for key in stats:
        if key in mapping:
            val = stats_c.pop(key)
            stats_c[mapping[key]] = val
    stats = stats_c

    logger.info('Opening DB session to %s', engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        logger.info("Checking if match %s exists in DB", match_id)
        if not session.query(Match).filter_by(match_id = match_id).all():
            ### If match doesn't exist, then we need to create it using a MatchData
            if not isinstance(_match, match.MatchData):
                _match = match.MatchData(_match, no_comms=True)

            match_object = Match(
                match_id = int(stats['match_id']),
                match_title = f"{_match.series_name}-{_match.match_title}",
                date = stats.pop('date'),
                team_1 = int(_match.team_1['team_id']),
                team_2 = int(_match.team_2['team_id']),
                team_1_players = str([player['player_id'] for player in _match.team_1_players]),
                team_2_players = str([player['player_id'] for player in _match.team_2_players]),
                ground = int(stats.pop('ground')),
                continent = stats.pop('continent'),
                match_url = _match.match_url,
                result = _match.result,
                total_innings = len(_match.innings_list),
                toss = int(_match.toss_winner),
                match_winner = int({
                    _match.team_1['team_abbreviation']:_match.team_1['team_id'],
                    _match.team_2['team_abbreviation']:_match.team_2['team_id'],
                }[_match.match_winner]),
                status = _match.status
            )
            session.add(match_object)
        else:
            stats.pop('date')
            stats.pop('ground')
            stats.pop('continent')

        for key in stats:
            try:
                if key == 'bowl_overs':
                    continue
                stats[key] = int(stats[key])
            except (ValueError, TypeError):
                pass

        stats.pop('team')
        stats.pop('opposition')

        # Logically you should only reach this part of the stats if the DB is not being queried,
        # in which case the match object is available and the player map can be executed.
        if not isinstance(_match, match.MatchData):
            _match = match.MatchData(_match, no_comms=True)

        if is_object_id: #Change from object id to player id
            player_object_id = player_id
            player_id = int(get_player_map(_match, 'player_id', 'object_id')[int(player_object_id)])
        else:
            player_object_id = int(get_player_map(_match, 'object_id', 'player_id')[int(player_id)])
        
        stat_id = f"{player_id}{match_id}{stats['inning']}"
        
        if stat_db_record_exists(player_id=player_id, match_id=match_id, stats=stats, stat_id=stat_id) and not force:
            logger.info('Skipping DB save as stat exists')
            return

        db_object = PlayerMatchStats(**{
            **{'stat_id':int(stat_id), 'player_id':int(player_id), 'player_object_id':int(player_object_id)},
            **stats
        })
    
        
        if is_object_id:
            PLAYER_SEARCH = {'player_object_id':player_id}
        else:    
            PLAYER_SEARCH = {'player_id':player_id}

        logger.debug("Checking if innings entry exists")
        try:
            logger.debug("Innings exists in database, this will be deleted and replace")
            inning = session.query(PlayerMatchStats).filter_by(stat_id=stat_id).all()[0]
        # inning = session.query(PlayerMatchStats).filter_by(**PLAYER_SEARCH).filter_by(match_id=match_id).filter_by(inning=stats['inning']).all()
            session.delete(inning)
        except IndexError:
            logger.debug("Innings did not exist in database")
        session.add(db_object)    
        session.commit()


def analyse_batting_inning(contributuion:pd.DataFrame):
    try:
        player_id = contributuion.batsmanPlayerId.value_counts().index[0]
    except IndexError:
        player_id = None

    if contributuion.empty:
        return NULL_BATTING_ANALYSIS

    def safe_divide(numerator, denominator, _round=2):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                return round(numerator/denominator, 2)
        except ZeroDivisionError:
            return float('inf')

    runs = contributuion.batsmanRuns.sum()
    try:
        _how_out = how_out(contributuion.iloc[-1].dismissalType)
    except IndexError:
        _how_out = False
    dismissals = bool(_how_out) #we assume that the dismissal is always at the end of an inning
    # dismissals = contributuion[(contributuion.dismissedBatsman == player_id)&(contributuion.isWicket == True)].count().isWicket
    balls = contributuion[(contributuion.batsmanPlayerId == player_id) & (contributuion.wides == 0)].shape[0]
    strike_rate = safe_divide(runs, balls)
    dot_balls = contributuion[contributuion.batsmanRuns == 0.0].count().batsmanRuns
    ones = contributuion[contributuion.batsmanRuns == 1.0].count().batsmanRuns
    twos = contributuion[contributuion.batsmanRuns == 2.0].count().batsmanRuns
    threes = contributuion[contributuion.batsmanRuns == 3.0].count().batsmanRuns
    fives = contributuion[contributuion.batsmanRuns == 5.0].count().batsmanRuns
    fours = contributuion[contributuion.isFour == True].count().isFour
    sixes = contributuion[contributuion.isSix == True].count().isSix
    average = safe_divide(runs, dismissals)
    try:
        total_balls_faced = contributuion.iloc[-1].batsmanBallsFaced if not isnan(contributuion.iloc[-1].batsmanBallsFaced) else contributuion.iloc[-2].batsmanBallsFaced
    except IndexError:
        total_balls_faced = 0
    fours_per_ball = safe_divide(fours, balls)
    sixes_per_ball = safe_divide(sixes, balls)
    dots_per_ball = safe_divide(dot_balls, balls)
    not_out = not contributuion['isWicket'].iloc[-1]
    #In control, out of control
    return {
        'runs': runs,
        'dismissals': dismissals,
        'balls_faced':balls,
        'sr':strike_rate,
        'average': average,
        'dot_balls': dot_balls,
        'ones': ones, 
        'twos':twos,
        'threes': threes, 
        'fours': fours,
        'fives': fives,
        'sixes': sixes,
        'how-out': _how_out,
        'not_out': not_out,
        'total_balls_faced': total_balls_faced,
        'fours_per_ball': fours_per_ball,
        'sixes_per_ball': sixes_per_ball,
        'dots_per_ball': dots_per_ball
    }

def aggregate_batting_analysis(batting_stats, cricket_runs_ave=True):
    """Takes list of batting stat objects and returns aggregate stats"""
    batting_stats_ = [x for x in batting_stats if x and x['runs'] != None] #this is wrong, this doesnt consider 0
    
    averages = {}
    totals = {}
    keys = list(batting_stats_[0].keys())
    for key in keys:
        try:
            total = sum([i[key] for i in batting_stats_])
            av = total/len(batting_stats)
            totals[key] = total
            averages[key] = round(av,2)
        except TypeError as e:
            pass
        except ZeroDivisionError:
            av = float('inf')

    if cricket_runs_ave and 'runs' in keys:
        runs = 0
        not_outs = 0
        for stat in batting_stats_:
            try:
                runs += stat['runs']
                if stat['not_out']:
                    not_outs += 1
            except TypeError:
                logger.debug('Problem with statline when calculating averages\n%s', stat)
                
        runs = runs/(len(batting_stats_) - not_outs)
        averages['runs'] = runs 

    return averages, totals

def analyse_batting(contributions):
    stats = []
    for contribution in contributions:
        if len(contribution) == 0:
            stats.append({})
            continue
        stats.append(analyse_batting_inning(contribution))
    
    averages, totals = aggregate_batting_analysis(stats)

    return averages, totals, stats


def check_runout_while_nonstriker(commentary_df:pd.DataFrame, player_id, match_object, is_object_id = False):
    if not isinstance(player_id, int):
        player_id = int(player_id)
    
    if is_object_id:
        player_id = get_player_map(match_object, 'player_id', 'object_id')[int(player_id)]
    
    wickets = commentary_df[commentary_df.isWicket == True]
    wickets = wickets[wickets.batsmanPlayerId != int(player_id)]
    
    player_name = get_player_map(match_object, 'known_as')[int(player_id)].lower()
    # player_name_split = player_name.split()
    # if len([player_name]) == player_name_split:
    #     player_names = player_name.split('-')
    # else: 
    #     player_names = player_name_split
    
    # contractions = ['ul', 'al', 'du']
    # for contraction in contractions:
    #     try:
    #         player_names.remove(contraction)
    #     except ValueError:
    #         pass

    for i,wicket in wickets.iterrows():
        if player_name in wicket.dismissalText.lower():
            if 'run out' in wicket.dismissalText.lower():
                if int(get_player_team(player_id, match_object)['team']) == int(wicket.battingTeam):
                    wicket['dismissedBatsman'] = player_id
                    return i, wicket
        # if len(wicket.commentTextItems.split()) < 10:
        #     raise utils.NoMatchCommentaryError
        # if any(name in wicket.commentTextItems.lower() for name in player_names):
        #     if int(player_id) != wicket.batsmanPlayerId:
        #         if int(get_player_team(player_id, match_object)['team']) == int(wicket.battingTeam):
        #             return i, wicket
    return None, pd.DataFrame()

def get_player_contributions(player_id:str or int, matches:list[match.MatchData], _type = 'both', by_innings = False, is_object_id=False):
    if matches == None:
        if is_object_id:
            matches = [int(m) for m  in wsf.get_player_match_list(player_id)]
        else:
            raise Exception('Match list not provided. Note: If player id is not object id, match list must be provided')
    if not isinstance(matches, Iterable):
        matches = [matches]
    
    contributions = []

    for _match in matches:
        try:
            if not isinstance(_match, match.MatchData):
                _match = match.MatchData(_match)

            contr_comms = _get_player_contribution(player_id=player_id, _match=_match, _type=_type, by_innings=by_innings, is_object_id=is_object_id)
            for inning in contr_comms:
                if not inning.empty:
                    contributions.append(inning)
        except utils.NoMatchCommentaryError:
            continue
    return contributions

def _get_player_contribution(player_id:str or int, _match:match.MatchData, _type = 'both', by_innings = False, is_object_id=False):
    """
    Get player innings from a match commentary
    """
    if not isinstance(player_id, int):
        player_id = int(player_id)
    
    if not isinstance(_match, match.MatchData):
        _match = match.MatchData(_match)

    try:
        check_player_in_match(player_id, _match, is_object_id)
    except utils.PlayerNotPartOfMatch:
        return []

    if is_object_id:
        player_id = get_player_map(_match, 'player_id', 'object_id')[int(player_id)]

    comms = pre_transform_comms(_match)
    # Checking runout from non-strikers end
    i = None
    if _type in ['both', 'bat']:
        i, runout_nonstrikers_df = check_runout_while_nonstriker(comms, player_id, _match, is_object_id=False)

    if _type == 'both':
        comms = comms[(comms['batsmanPlayerId'] == int(player_id)) | (comms['bowlerPlayerId'] == int(player_id))]
    else:
        if _type == 'bat':
            col = 'batsmanPlayerId'
        elif _type == 'bowl':
            col = 'bowlerPlayerId'
        comms = comms[comms[col] == int(player_id)]

    if i:
        comms.loc[i] = runout_nonstrikers_df

    # Add batsman ball faced number in df and also bowler total balls bowled until this point
    try:
        inning_numbers = [i for i in set(comms['inningNumber'])]
        inning_num_index = 0
        contr_index = 1
        for i,row in comms.iterrows():
            if row.inningNumber != inning_numbers[inning_num_index]:
                contr_index = 1
                inning_num_index += 1

            if int(player_id) == int(row.batsmanPlayerId):
                comms.at[i, 'batsmanBallsFaced'] = contr_index
                # row['batsmanBallsFaced'] = contr_index
                contr_index += 1
            if int(player_id) == int(row.bowlerPlayerId):
                comms.at[i, 'bowlerBallsBowled'] = contr_index
                contr_index += 1
    except ValueError:
        pass

    if by_innings:
        try:
            comms = [comms[comms['inningNumber'] == j+1] for j, _ in enumerate(_match.innings_list) if not comms[comms['inningNumber'] == j+1].empty]
        except TypeError:
            comms = [comms[comms['inningNumber'] == j+1] for j, _ in enumerate(_match.innings) if not comms[comms['inningNumber'] == j+1].empty]
        # for i, _ in enumerate(match.innings_list):
        #     _comms.append(comms[comms['inningNumber'] == i])
        # _comm
    
    return comms

def get_cricket_totals(player_id, matches=None, _type='both', by_innings=False, is_object_id=False, from_scorecards=False, keep_dismissal_codes=False, save=True, try_local=True, force=False):
    if not isinstance(player_id, int):
        player_id = int(player_id)
    
    if matches == None:
        if is_object_id:
            matches = [int(m) for m  in wsf.get_player_match_list(player_id)]
        else:
            raise Exception('Match list not provided. Note: If player id is not object id, match list must be provided')
    if not isinstance(matches, Iterable):
        matches = [matches]
    
    contributions = []

    for _match in matches:
        logger.info('Getting player contributions for match %s', _match)
        match_save = save
        if force:
            logger.debug('Forcing save of stats as "force" flag set to "True"')
            match_save = True
        try:
            contribution, in_db = _cricket_totals(player_id, _match, _type, by_innings, is_object_id, from_scorecards=from_scorecards, keep_dismissal_codes=keep_dismissal_codes, try_local=try_local)
            if in_db:
                if not force:
                    logger.info('Skipping DB save as stat exists in DB')
                    match_save = False
            if _type == 'both':
                for i,inning in enumerate(contribution['bat']+contribution['bowl']):
                    if 'wickets' in inning: #Need know if the contribution is batting or bowling
                        contr_type = 'bowl'
                    else:
                        contr_type = 'bat'
                    stats = {**inning, **{key:contribution[key] for key in contribution.keys() if key not in ['bat', 'bowl']}, **{'type':contr_type}}
                    contributions.append(stats)
                    if match_save:
                        save_player_stats_to_db(stats.copy(), player_id, _match, is_object_id)
                    # contributions.append({**contribution['bowl'], **{key:contribution[key] for key in contribution.keys() if key not in ['bat', 'bowl']}})
            else:
                for i,inning in enumerate(contribution[_type]):
                    stats = {**inning, **{key:contribution[key] for key in contribution.keys() if key not in ['bat', 'bowl']}, **{'type':_type}}
                    contributions.append(stats)
                    if match_save:
                        save_player_stats_to_db(stats.copy(), player_id, _match, is_object_id)
        except cricketerrors.MatchNotFoundError:
            logger.warning('Match ID: %s not found', _match)
    return contributions

def _cricket_totals(player_id, m:match.MatchData or int, _type='both', by_innings=False, is_object_id=False, from_scorecards=False, keep_dismissal_codes=False, try_local=True):
    """
    Get the cricketing totals for the players. I.e. their stats in the collected innings.
    """
    if not isinstance(player_id, int):
        player_id = int(player_id)

    try:
        logger.info("Getting player totals for match: %s Player: %s", m.match_id, player_id)
    except AttributeError:
        logger.info("Getting player totals for match: %s Player: %s", m, player_id)

    batting_figures = None
    bowling_figures = None
    in_db = False

    if try_local:
        logger.info("Getting match details from DB")
        _match = get_match_details_from_db(m)
        if _match:
            date = _match['date']
            continent = _match['continent']
            ground = _match['ground']
            if str(player_id) in _match['teams'][0]:
                team = _match['team_1']
                opps = _match['team_2']
            else:

                team = _match['team_2']
                opps = _match['team_1']
        else:
            logger.info("Match not found in DB, match and player data will be collected from JSON")
            try_local = False
    # if player id in bowling id, update bowling figures
    if not isinstance(m, match.MatchData):
        if not try_local:
            m = match.MatchData(m)
    
    if not try_local:
        # if is_object_id: #Change from object id to player id
        #     player_id = int(get_player_map(m, 'player_id', 'object_id')[int(player_id)])
        date = datetime.strptime(m.date, "%Y-%m-%d")
        teams = get_player_team(player_id, m, is_object_id=is_object_id)
        team = teams['team']
        opps = teams['opposition']
        continent = m.continent
        ground = m.ground_id

    if _type != 'bat':
        bowling_figures = []
        try:
            """Handle figures from DB"""
            if try_local:
                logger.info("Trying DB to retrieve bowling figures")
                db_figures = get_figures_from_db(player_id, m, 'bowl', is_object_id=is_object_id)
                if db_figures:
                    for figures in db_figures:
                        if figures['overs']:
                            bowling_figures += [figures]
                            logger.info("Retrieved player bowling stats from DB for inning %s", figures['inning'])
                    raise utils.FiguresInDB
                logger.info("Bowling figures not found in DB")

            """Handle figures from scorecard"""
            if from_scorecards:
                raise utils.NoMatchCommentaryError

            """Handle figures from match JSON"""
            if not isinstance(m, match.MatchData):
                m = match.MatchData(m)
            bowling_dfs = _get_player_contribution(player_id, m, 'bowl', by_innings=by_innings, is_object_id=is_object_id)
            if is_object_id: #Change from object id to player id
                bowler_player_id = int(get_player_map(m, 'player_id', 'object_id')[int(player_id)])
            if not by_innings:
                bowling_dfs = pd.concat([bowling_dfs], ignore_index=True, axis=0)
            if not isinstance(bowling_dfs, list):
                bowling_dfs = [bowling_dfs]
            for bowling_df in bowling_dfs:
                try:
                    balls_bowled = bowling_df.shape[0]
                    bowling_df_agg = bowling_df[['batsmanRuns', 'bowlerRuns', 'noballs', 'wides', 'isSix', 'isFour', 'isWicket', 'legbyes']].sum(numeric_only=False)
                    extras = bowling_df_agg['wides']+bowling_df_agg['noballs']
                    inning = bowling_df['inningNumber'].iloc[0]
                    inning_bowling_figures = {
                        'inning':inning,
                        'overs': f'{(balls_bowled - extras)//6}.{(balls_bowled - extras)%6}',
                        'runs': bowling_df_agg['bowlerRuns'],
                        'dot_balls': (bowling_df['bowlerRuns'] == 0).sum(),
                        'wides': bowling_df_agg['wides'],
                        'noballs': bowling_df_agg['noballs'],
                        'wickets': bowling_df_agg['isWicket']
                    }
                    bowling_figures.append(inning_bowling_figures)
                except IndexError:
                    logger.debug('No bowling inning data for match %s player %s', m.match_id, player_id)
                    continue

        except utils.NoMatchCommentaryError:
            logger.info("Getting bowling figures from scorecard")
            bowling_figures += get_figures_from_scorecard(player_id, m, 'bowl', is_object_id=is_object_id)
        
        except utils.FiguresInDB:
            in_db = True

    if _type != 'bowl':
        batting_figures = []
        try:

            """Handle figures from DB"""
            if try_local:
                logger.info("Trying DB to retrieve batting figures")
                db_figures = get_figures_from_db(player_id, m, 'bat', is_object_id=is_object_id)
                if db_figures:
                    for figures in db_figures:
                        if figures['runs'] != None:
                            batting_figures += [figures]
                            logger.info("Retrieved player batting stats from DB for inning %s", figures['inning'])
                    raise utils.FiguresInDB
                logger.info("Batting figures not found in DB")
            
            """Handle figures from scorecard"""
            if from_scorecards:
                raise utils.NoMatchCommentaryError
            
            """Handle figures from match JSON"""
            if not isinstance(m, match.MatchData):
                m = match.MatchData(m)
            batting_dfs = _get_player_contribution(player_id, m, 'bat', by_innings=by_innings, is_object_id=is_object_id)
            if is_object_id: #Change from object id to player id
                batsman_player_id = int(get_player_map(m, 'player_id', 'object_id')[int(player_id)])
            if not by_innings:
                batting_dfs = pd.concat([batting_dfs], ignore_index=True, axis=0)
            if not isinstance(batting_dfs, list):
                batting_dfs = [batting_dfs]
            for batting_df in batting_dfs:
                try:
                    not_out = not batting_df['isWicket'].iloc[-1]
                    balls_faced = batting_df[(batting_df.batsmanPlayerId == batsman_player_id) & (batting_df.wides == 0)].shape[0]
                    batting_df_agg = batting_df[batting_df.batsmanPlayerId == batsman_player_id].sum()
                    inning = batting_df['inningNumber'].iloc[0]
                    inning_batting_figures = {
                        'inning': inning,
                        'runs': batting_df_agg['batsmanRuns'],
                        'balls_faced': balls_faced,
                        'fours': batting_df_agg['isFour'],
                        'six': batting_df_agg['isSix'],
                        'dot_balls': (batting_df[(batting_df.batsmanPlayerId == batsman_player_id) & (batting_df.wides == 0)]['bowlerRuns'] == 0).sum(),
                        'not_out': not_out,
                        'how_out': how_out(batting_df.iloc[-1].dismissalType, keep_code=keep_dismissal_codes)
                    }
                    batting_figures.append(inning_batting_figures)
                except IndexError:
                    logger.debug('No batting inning data for match %s player %s', m.match_id, player_id)
                    continue
        except utils.NoMatchCommentaryError:
            logger.info("Getting batting figures from scorecard")
            batting_figures += get_figures_from_scorecard(player_id, m, 'bat', is_object_id=is_object_id)
        except utils.FiguresInDB:
            in_db = True
    
    try:
        logger.debug("Match ID: %s\nBatting: %s\nBowling: %s",m.match_id, batting_figures, bowling_figures) 
        return {'bat': batting_figures, 'bowl': bowling_figures, 'date':date,'team':team, 'opposition': opps, 'ground':ground, 'continent':continent, 'match_id': m.match_id}, in_db
    except AttributeError:
        logger.debug("Match ID: %s\nBatting: %s\nBowling: %s",m, batting_figures, bowling_figures)
        return {'bat': batting_figures, 'bowl': bowling_figures, 'date':date,'team':team, 'opposition': opps, 'ground':ground, 'continent':continent, 'match_id': m}, in_db
    

def process_text_comms(df:pd.DataFrame, columns = ['dismissalText', 'commentPreTextItems', 'commentTextItems', 'commentPostTextItems', 'commentVideos']):
    for column in columns:
        df[column] = df[column].map(process_text_values)
        df[column] = df[column].map(remove_html)

def remove_html(value):
    try:
        matches = re.findall('[^<>]{0,}(<[^<>]+>)[^<>]{0,}', value)
        for match in matches:
            value = value.replace(match, '')
        value = value.capitalize()
    except TypeError:
        pass
    finally:
        return value

def process_text_values(value):
    if not isinstance(value, list):
        value = [value]
    try:
        value = value[0]
        if 'type' in value.keys():
            if value['type'] == 'HTML':
                return value['html']
        else:
            return value['commentary']
    except (TypeError, KeyError, AttributeError):
        if value is None:
            return 'None'
        # print('Unhandled value', value)
        pass
    except IndexError:
        return 'None'

def create_dictionary(words, reverse = False):
    dictionary = {}
    for word in words:
        if word in dictionary:
            dictionary[word] += 1
        else:
            dictionary[word] = 1
    return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse= not reverse))

def create_vocabulary(df, m, remove_match_refs = True):
    player_list = list(get_player_map(m, map_column='known_as').values())
    player_list = [name.lower() for player in player_list for name in player.split()]

    words = []
    for entry in df['commentTextItems']:
        entry = entry.translate(str.maketrans('', '', string.punctuation))
        entry = entry.split()
        if remove_match_refs:
            words += [e.lower() for e in entry if e not in player_list]
        else:
            words += [e.lower() for e in entry]

    dictionary = create_dictionary(words)
    return dictionary

def create_dummies(df: pd.DataFrame, column = 'batsmanRuns', value_mapping = {'isRuns': [1,2,3,5]}):
    for value in value_mapping:
        df[value] = df[column].isin(value_mapping[value])

def create_labels(df: pd.DataFrame, categories:list, null_category:str, rev_dummy_col_name:str = 'labels', commentary_col = 'commentTextItems', inplace = False):
    if not inplace:
        result = df.loc[:, categories+[commentary_col]]
    else:

        result = df
    logger.info(f'Creating labels for commentary. \n \
                 Columns to label: {", ".join(categories)} \n \
                 Commentary text column: {commentary_col}')
    result.loc[:, null_category] = False
    categories += [null_category]
    logger.debug('Reverse dummy to create labels column')
    for index, row in result.iterrows():
        if int(row.loc[categories].max()) == 0:
            result.at[index, null_category] = True
    reverse_dummy = result[categories].idxmax(axis=1)
    reverse_dummy = reverse_dummy.to_frame(name= rev_dummy_col_name)
    logger.debug('Creating label dataframe')
    if not inplace:
        #print(result.head())
        reverse_dummy[commentary_col] = result[commentary_col]
        return reverse_dummy
    else:
        result[rev_dummy_col_name] = reverse_dummy[rev_dummy_col_name]
        return result

def cat_to_num(labels, label_names):
    mapping = {cat:i for i,cat in enumerate(label_names)}
    labels_nums = [mapping[label] for label in labels]
    return labels_nums

def package_data(data:list, labels:list, label_names:list = [], encode_num = True):
    if not label_names:
        label_names = set(labels)
        label_names = list(label_names)
    if encode_num:
        labels = np.array(cat_to_num(labels, label_names))
    packaged_data = sklearn.utils.Bunch(
        data = list(data), labels = labels, label_names = list(label_names)
    )
    return packaged_data

def describe_data_set(dataset, title, label_names=None):
    if isinstance(dataset, sklearn.utils.Bunch):
        labels_unmapped = [dataset.label_names[label] for label in dataset.labels]
    else:
        labels_unmapped = [label_names[label] for label in dataset]
    series = pd.Series(labels_unmapped, )
    groups = series_to_df(series, [title,'labels']).groupby('labels').count()/series.shape[0]
    return groups

def calculate_running_average(innings_df):
    """Calculate running average for input innings. Returns list of running average"""
    if innings_df.empty:
        logger.info('No innings for player')
        return None

    _running_average = []
    innings_df = innings_df[innings_df.runs.notna()]
    total_runs = 0
    out = 0

    for innings in zip(innings_df.runs, innings_df.not_out):
        total_runs += innings[0]
        if innings[1] == False:
            out += 1
        try:
            _running_average.append(round(total_runs/out,2))
        except ZeroDivisionError:
            _running_average.append(None)

    return _running_average

def calculate_recent_form_average(innings_df:pd.DataFrame, window_size=12):
    """Calculate recent form average for input innings. Returns list of recent form average"""
    
    if innings_df.empty:
        logger.info('No innings for player')
        return None

    last_x_average = []
    innings_df = innings_df[innings_df.runs.notna()]
    window_runs = 0
    window_out = 0

    for i,innings in enumerate(zip(innings_df.runs, innings_df.not_out)):
        if i>=window_size:
            window_runs -= innings_df.runs.iloc[i-window_size]
            if innings_df.not_out.iloc[i-window_size] == False:
                window_out -= 1
        
        window_runs += innings[0]
        if innings[1] == False:
            window_out += 1
        try:
            last_x_average.append(round(window_runs/window_out,2))
        except ZeroDivisionError:
            last_x_average.append(None)

    return last_x_average

def get_running_average(player_id, innings = None, match_list=None, _format='test'):
    if innings is None:
        if match_list is None:
            match_list = wsf.get_player_match_list(player_id, _format=_format, match_links=False)
        innings = get_cricket_totals(player_id, match_list, _type='bat', by_innings=True, is_object_id=True)
    #innings = [inning for match in contributions for inning in match]
    innings_df = pd.DataFrame(innings)
    average = calculate_running_average(innings_df)
    return average

def get_recent_form_average(player_id, innings=None, match_list=None, window_size=10,_format='test'):
    if innings is None:
        if match_list is None:
            match_list = wsf.get_player_match_list(player_id, _format=_format, match_links=False)
        innings = get_cricket_totals(player_id, match_list, _type='bat', by_innings=True, is_object_id=True)
    # innings = [inning for match in contributions for inning in match]
    innings_df = pd.DataFrame(innings)
    average = calculate_recent_form_average(innings_df, window_size=window_size)
    return average

def percentagize_x_axis(data, _round = 2):
    length = len(data)
    return [round(x*(100/length), _round) for x in range(length)]

def normalized_career_length(career_data:dict):
    """
    Takes a variable length career and normalizes it to the same length
    Returns a df where columns indicate an individual career and rows are the percentage of the career completed
    """
    #recent_form_df = {}
    #max_length = career_data.index(max(career_data, key=len))
    #index = set([i for data in career_data for i in percentagize_x_axis(data)])
    #index = sorted(index)
    full_df = pd.concat([pd.DataFrame(career_data[data], index=percentagize_x_axis(career_data[data]), columns=[data]) for data in career_data], axis=1)
    full_df.sort_index(inplace=True)
    return full_df

def apply_aggregate_func_to_list(player_id_list, _funcs, player_ages=None, dates = None, return_innings = False, disable_logging=True, **kwargs):
    """
    Apply an aggregation function such as running average, to a list of players, returns a df of the aggregate functions
    
    player_id_list: list of player ids, these should be cricinfo object IDs
    dates: (optional) The dates between which the careers should be graphed, date format YYYY-MM-DD:YYYY-MM-DD
    player_ages: (optional) Retrieve stats for player when they are within a certain age range Format Start Age:End Age
    return_innings: Returns the innings objects as well as the calculated stats
    disable_logging: Disables logging during the execution of the function
    **kwargs: To be passed to the aggregate functions

    Returns: Dict of results:
    {
        function_name:{
            player_id:agg_function_result
        },
        'innings_totals':{
            player_id:innings_df
        }
    }
    """
    if player_ages:
        if not isinstance(player_ages, list):
            player_ages = [player_ages]
        if len(player_ages) == 1:
            player_ages = player_ages*len(player_id_list)
        if len(player_ages) != len(player_id_list):
            player_ages = player_ages + [':']*abs(len(player_ages) != len(player_id_list))
            player_ages = player_ages[:len(player_id_list)]
    else:
        player_ages = [None for i in range(len(player_id_list))]

    logger.disabled = disable_logging
    applied_values = defaultdict(dict)
    for i,player in enumerate(player_id_list):
        if not dates:
            dates = dates_from_age(player, player_ages[i])
        player_match_list = wsf.get_player_match_list(player, dates=dates)
        player_innings_df = get_cricket_totals(player, player_match_list, _type='bat', by_innings=True, is_object_id=True)
        player_innings_df = pd.DataFrame(player_innings_df)
        for _func in _funcs:
            function_name = re.search('function ([\_a-zA-Z]+) at', str(_func)).group(1)
            applied_values[function_name][player] = _func(player_innings_df, **kwargs)
        if return_innings:
            applied_values['innings_totals'][player] = player_innings_df
    if disable_logging:
        logger.disabled = not disable_logging
    
    return applied_values

def get_dismissal_descriptions(commentary):
    all_dismissals = []
    for match in commentary:
        comms = match.iloc[-1]
        
        if comms.dismissalText not in [None, 'null', 'NaN', 'None']:
            logger.debug('Dismissal commentary: %s, %s', comms.commentTextItems, comms.dismissalText)
            all_dismissals.append((comms.commentTextItems, comms.dismissalText))
        else:
            logger.debug("Batsman was not dismissed in match, %s", comms.commentTextItems)

    return all_dismissals

def search_for_phrases(text_items, keywords = [], exclude_words = [], primary_keywords = [], threshold=0.5):
    
    def search_word(word, text, lower=True, no_punc=False):
        if lower:
            text = text.lower()
        if no_punc:
            text = text.translate(str.maketrans('', '', string.punctuation))
        m = re.search(word, text)
        if m:
            return True
        else:
            return False

    def update_word_score(score, weight = None, exclude=False):
        if exclude:
            if not weight:
                weight = -1
            if weight > 0:
                weight = -weight
            return max(0, score+weight)
        
        else:
            if not weight:
                weight = 0.5
            return min(1, score+weight)
    
    scores = [0]*len(text_items)
    indices = [0]*len(text_items)
    logger.debug('Finding text with matching words %s', keywords)
    logger.debug('Exluding text if contains %s', exclude_words)

    for i, text in enumerate(text_items):
        score = 0
        dealt_with = False
        for word in primary_keywords:
            if isinstance(word, str):
                word = (word, None)
            if search_word(word[0], text):
                logger.debug("Matching text: %s", text)
                indices[i] = 1
                score = 1
                dealt_with = True
        
        if not dealt_with:
            for word in keywords:
                if isinstance(word, str):
                    word = (word, None)
                if search_word(word[0], text):
                    try:
                        score = update_word_score(score=score, weight=word[1])
                    except TypeError:
                        score = update_word_score(score=score)
                
                #print(word, score)
            
            for word in exclude_words:
                if isinstance(word, str):
                    word = (word, None)
                
                if search_word(word[0], text):
                    try:
                        score = update_word_score(score=score, weight=word[1], exclude=True)
                    except TypeError:
                        score = update_word_score(score=score, exclude=True)
                    #print(word, score)
                    if score == 0:
                        break
            
            if score >= threshold:
                indices[i] = 1

        scores[i] = score
    
    return indices, scores


def search_for_keywords(text_items, keywords = [], exclude_words = [], primary_keywords = [], return_matching = False, return_indices = False):
    """
    Searches for keywords in the text_item
    
    Returns: (count, matching_items, indices)
    """
    count = 0
    matching = []
    indices = []
    logger.debug('Finding text with matching words %s', keywords)
    logger.debug('Exluding text if contains %s', exclude_words)
    for i, text in enumerate(text_items):
        dealt_with = False
        for word in primary_keywords:
            if word in text.lower():
                count += 1
                logger.debug("Matching text: %s", text)
                matching.append(text)
                indices.append(i)
                dealt_with = True
        
        if not dealt_with:
            for word in keywords:
                if word in text.lower():
                    exclude = False
                    for e_word in exclude_words:
                        if e_word in text.lower():
                            exclude = True
                            break
                    if exclude:
                        logger.debug("Matching text with exlusion: %s", text)
                        break
                    count += 1
                    logger.debug("Matching text: %s", text)
                    matching.append(text)
                    indices.append(i)
                    break
                else:
                    logger.debug("No matches in text: %s", text)
        else:
            dealt_with = False
            continue

    return_object = [count]
    if return_matching:
        return_object.append(matching)
    else:
        return_object.append(None)
    
    if return_indices:
        return_object.append(indices)
    else:
        return_object.append(None)
    return tuple(return_object)

def cumulative_sr(inning_comms:pd.DataFrame):
    """Calculates the cumulative strike rate through the innings"""
    
    tot_runs = 0
    tot_balls = 0

    cum_sr = []

    for i, row in inning_comms.iterrows():
        tot_runs += row.batsmanRuns
        if not row.wides or not row.noballs:
            tot_balls += 1

        sr = tot_runs/tot_balls
        cum_sr.append(sr)
    
    return cum_sr

def average_elements_of_list(list_of_lists:list[list]):
    """
    Average each element of a list over all the lists. Can handle lists of varying lengths.
    Only the lists with element in ith position are considered in average
    """
    
    max_length = len(max(list_of_lists, key=lambda x: len(x)))

    averaged_list = []
    for i in range(max_length):
        element_tot = 0
        element_count = 0
        for _list in list_of_lists:
            try:
                element_tot += _list[i]
                element_count += 1
            except IndexError:
                pass
        
        averaged_list.append(element_tot/element_count)

    return averaged_list

def get_player_performances_in_periods(player_id, min_period, max_period = None, cricket_totals = None, _format='test', _type='bat', cricket_runs_ave=True):
    """
    Returns the player stats in time periods defined by the minimum to maximum period lengths
    Note: player_id is object_id
    If there is no max period, then the only the single minimum period value will be calculated

    Returns: dict of periodic stats
    {period:{start_inning:end_inning:{average:ave_dict, totals: tots_dict, innings: period_innings}}}
    """
    if not max_period:
        max_period = min_period + 1
    
    periodic_stats = {}
    if not cricket_totals:
        matches = wsf.get_player_match_list(player_id, _format=_format)
        cricket_totals = get_cricket_totals(player_id, matches, _type=_type, by_innings=True, is_object_id=True)

    for period in range(min_period, max_period):    
        periodic_stats[period] = {}

        for i in range(len(cricket_totals)-period + 1):

            period_match_totals = cricket_totals[i:(i+period)]
            period_ave, period_tot = aggregate_batting_analysis(period_match_totals, cricket_runs_ave=cricket_runs_ave)
            periodic_stats[period][f'{i}:{i+period}'] = {'averages':period_ave, 'totals':period_tot, 'innings': period_match_totals}
    
    return periodic_stats

def get_best_periods(player_id, min_period=1, max_period=None, display_key=None, stat_type='averages', stat='runs', lowest=False, _format='test', _type='bat', periodic_stats=None):
    """
    Gets the best metric in each period in periodic stats. If periodic stats are provided then no period needs to be provided
    """
    if not periodic_stats:
        periodic_stats = get_player_performances_in_periods(player_id, min_period, max_period, _format=_format, _type=_type)

    agg_func = max
    if lowest:
        agg_func = min
    
    agg_stat_in_periods = [agg_func(periodic_stats[period], key=lambda x: periodic_stats[period][x][stat_type][stat]) for period in periodic_stats] #Extracting the max/min stat in the period 
    agg_stat_in_periods = [(periodic_stats[list(periodic_stats.keys())[i]][period][stat_type][stat], period) for i,period in enumerate(agg_stat_in_periods)] #Get period max stat occured in
    
    return {x[0]:x[1] for x in zip([key for key in periodic_stats], agg_stat_in_periods)} 

def search_shots_in_comms(contributions, search_keywords, exlude_words=[], primary_keywords=[], threshold = 0.5):
    """Search for a particular shot in a set of commentary and return commentary df where the shot was played"""
    shots = []
    for i, comms in enumerate(contributions):
        innings = comms.commentTextItems.to_list()
        search = search_for_phrases(innings, keywords=search_keywords, exclude_words=exlude_words, primary_keywords=primary_keywords, threshold = threshold)
        shots.append(comms.iloc[[i for i,x in enumerate(search[0]) if x == 1]])
        
    return shots

def graph_shot_runs(shot_stats, full_innings, shot_name, colours=['#5f187f','#f8765c']):
    runs = []
    for i in range(len(full_innings)):
        r = {'runs':shot_stats[i]['runs'], 'type':shot_name,'inning':i}
        r2 = {'runs':full_innings[i]['runs'], 'type':'total','inning':i}
        runs.append(r2)
        runs.append(r)

    runs_df = pd.DataFrame(runs)

    fig, ax1 = plt.subplots(figsize=(30,20)) 
    colours = colours
    custom = sns.set_palette(sns.color_palette(colours))
    sns.barplot(data = runs_df, x=runs_df.inning, y=runs_df.runs, alpha=0.8, ax=ax1, palette=custom, hue=runs_df.type, dodge=False)
    ax1.set_xticklabels(labels=[x for x in range(len(full_innings))], rotation=90);
    ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax1.margins(x=0)

    return fig, runs_df

def get_cumulative_dismissals(batting_stats):
    """Given a dict of batting stats, returns the cumulative dismissal arrays of those stats"""
    
    dismissals = {}

    for i,stat in enumerate(batting_stats):
        
        try:
            dismissals[stat['how_out']].append(dismissals[stat['how_out']][-1] + 1)
        except KeyError:
            dismissals[stat['how_out']] = [0]*i
            dismissals[stat['how_out']].append(1)

        for key in dismissals:
            if key != stat['how_out']:
                dismissals[key].append(dismissals[key][-1])

    return dismissals

def fraction_of_total(shot_stats, full_innings, key):
    perc_of_total = []
    for i in range(len(full_innings)):
        try:
            perc_of_total.append(round(int(shot_stats[i][key])/int(full_innings[i][key]), 2))
        except ZeroDivisionError:
            perc_of_total.append(0)

    return perc_of_total

def moving_average(nums, window_size=5):
    last_x_average = [None]*(window_size)

    for i in range(len(nums)-window_size):
        last_x_average.append(round(sum(nums[i:i+window_size])/window_size, 5))

    return last_x_average

def cumulative_average(nums):
    total = 0
    cum_average = []

    for i, x in enumerate(nums):
        total += x
        bf = total/(i+1)
        cum_average.append(bf)
    
    return cum_average

def extract_scoring_rates(tests, post_tests = [], period=None):
    """
    Extract the scoring rates from list of test matches.
    
    Inputs
    ------

    tests: List of test match id's to extract dates from
    period: the period of aggregation. Can be year, month or None(which does it by day)
    """
    
    scoring_rates = {}
    for _match in tests:
        m = match.MatchData(_match, no_comms=True)
        date = datetime.strptime(m.date, '%Y-%m-%d')
        if period == None:
            date = m.date
        if period == 'month':
            date = datetime.strftime(date, '%Y-%m')
        if period == 'year':
            date = datetime.strftime(date, '%Y')
        rates = [x['run_rate'] for x in m.innings]
        try:
            scoring_rates[date][0]+=rates
            scoring_rates[date][1]+=len(rates)
        except KeyError:
            scoring_rates[date] = [[],0]
            scoring_rates[date][0]=rates
            scoring_rates[date][1]=len(rates)

    # post_scoring_rates = {}
    # for _match in post_tests:
    #     m = match.MatchData(_match, no_comms=True)
    #     date = datetime.strptime(m.date, '%Y-%m-%d')
    #     if period == None:
    #         date = m.date
    #     if period == 'month':
    #         date = datetime.strftime(date, '%Y-%m')
    #     if period == 'year':
    #         date = datetime.strftime(date, '%Y')
    #     scoring_rates = [x['run_rate'] for x in m.innings]
    #     try:
    #         post_scoring_rates[date][0]+=scoring_rates
    #         post_scoring_rates[date][1]+=len(scoring_rates)
    #     except KeyError:
    #         post_scoring_rates[date] = [[],0]
    #         post_scoring_rates[date][0] = scoring_rates
    #         post_scoring_rates[date][1] = len(scoring_rates)
    
    return scoring_rates

def resolve_scoring_rates_to_ave(scoring_rate):
    scoring_rate_aves_y = {}
    for date in scoring_rate:
        try:
            temp_soring_rates = []
            for rate in scoring_rate[date][0]:
                if rate:
                    temp_soring_rates.append(float(rate))
            scoring_rate_aves_y[date] = sum(temp_soring_rates)/len(temp_soring_rates)
        except:
            logger.debug("Error with scoring rate entry: %s:%s", date,  scoring_rate[date][0])
    
    return scoring_rate_aves_y

def average_innings(contributions):
    innings_lists = [list(x.batsmanRuns) for x in contributions]
    average_inning = average_elements_of_list(innings_lists)
    average_inning_runs = []
    runs = 0
    for run in average_inning:
        runs += run
        average_inning_runs.append(runs)
    
    return average_inning_runs