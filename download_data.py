import codebase.analysis_functions as af
import codebase.web_scrape_functions as wsf
from codebase.match_data import MatchData
import espncricinfo.exceptions
import pandas as pd
import re
import os
from utils import logger
from pprint import pprint
import pickle
import json
from utils import DATA_LOCATION
from bs4 import BeautifulSoup
from codebase.web_scrape_functions import create_retry_session
KOHLI_ID = '253802'

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

# error_players = []
# for player in ['373696']:
#     try:
#         logger.info("Grabbing match totals for player %s for the purposes of saving to DB")
#         totals = af.get_cricket_totals(int(player), _type='bat', by_innings=True, is_object_id=True, save=True)
#         logger.debug(totals)
#     except Exception as e:
#         logger.error("Error with player %s", player)
        
#         logger.exception("Catching literally any error and proceeding so that I can run this overnight, error this time was")
#         error_players.append(player)

# logger.info("Data collection task completed")
# logger.info("Error players are %s", str(error_players))
# kohli_matches = wsf.get_player_match_list(KOHLI_ID)
# kohli_comms = af.get_player_contributions(KOHLI_ID, kohli_matches, _type='bat', by_innings=True, is_object_id=True)
# with open(os.path.join(DATA_LOCATION, 'kohli_comms.p')) as _file:
#     pickle.dump(kohli_comms, _file)
# result = {}
# for player in top_players.Players:
#     match_list = wsf.player_match_list(player)
#     innings = af.get_cricket_totals(player, match_list, 'bat', True, True, True)
#     innings_df = pd.DataFrame(innings_df)
#     result[player] = af.calculate_running_average(innings_df)

def get_archive_url(season: str):
    season = season.replace('/', '%2F')    
    return f"https://www.espncricinfo.com/ci/engine/series/index.html?season={season};view=season"

def get_series_from_archive(season, match_type='First-class'):
    session = create_retry_session()
    url = get_archive_url(season)
    response = session.get(url)
    html = BeautifulSoup(response.content, 'html.parser')

    match_sections = html.find("div", {"class": "match-section-head"}, text=match_type).find_next_sibling("section").findChildren("section", {"class": "series-summary-block"})
    return [series["data-summary-url"] for series in match_sections]

def get_fixture_url_from_series_url(series_data_url):
    session = create_retry_session()
    url = f"https://espncricinfo.com{series_data_url}"
    response = session.get(url)
    html = BeautifulSoup(response.content, 'html.parser')

    fixtures_link = html.find("a", text="Fixtures & Results")
    return fixtures_link['href']

def get_matches_from_fixture_list(fixture_url):
    session = create_retry_session()
    url = fixture_url
    response = session.get(url)
    html = BeautifulSoup(response.content, 'html.parser')

    matches = html.find("div", {"class":"ds-mb-4"}).find_all("div", {"class":"ds-border-line-default-translucent"})
    #matches = html.find("div", {"class":"ds-flex ds-space-x-5"}).findChild().findChild.fin

    match_urls = [match.find_next("a")['href'] for match in matches]

    match_ids = []

    for url in match_urls:
        try:
            match_ids.append(re.search(pattern='(\d+)/full-scorecard', string=url)[1])
        except TypeError:
            try:
                match_ids.append(re.search(pattern='(\d+)/live-cricket-score', string=url)[1])
            except TypeError:
                logger.error("Match ID not found using regex pattern for urls: %s", url)
    
    return match_ids
        

def generate_player_match_dict(matches, save_every=100):
    players_dict={}
    for i, match_id in enumerate(matches):
        logger.debug('Match: %s', i)
        logger.debug('Match ID: %s', match_id)
        try:
            _match = MatchData(match_id)
        except (espncricinfo.exceptions.NoJSONData, espncricinfo.exceptions.NoScorecardError):
            logger.debug('Match %s has no JSON data...skipping', match_id)
            continue
        players = [x['object_id'] for x in _match.all_players]
        for player in players:
            logger.debug('Adding match %s for player %s', match_id, player)
            try:
                players_dict[player] += [match_id]
            except KeyError:
                players_dict[player] = [match_id]
        
        if (i+1)%save_every == 0:

            with open(os.path.join(DATA_LOCATION, 'player_match_dict.json'), 'w') as file:
                logger.info(f"Saved results from matches {i}/{len(matches)}")
                json.dump(players_dict, file)

    if save_every:
        logger.info("Saving final player match object")
        with open(os.path.join(DATA_LOCATION, 'player_match_dict.json'), 'w') as file:
            json.dump(players_dict, file)
                    
    return players_dict


def create_player_first_class_matches_dict(seasons, skip_gather_ids=False):
    if not skip_gather_ids:
        try:
            match_ids = []

            for season in seasons:
                logger.info("Getting season fixture list for %s", season)
                series_urls = get_series_from_archive(season)
                logger.info("Season series URL: %s", series_urls)
                series_fixture_lists = [get_fixture_url_from_series_url(series_url) for series_url in series_urls]
                logger.info("Season fixture URL: %s", series_fixture_lists)
                for fixture_list in series_fixture_lists:
                    match_ids += get_matches_from_fixture_list(fixture_list)
            
            with open(os.path.join(DATA_LOCATION, 'first_class_match_ids.json'), 'w') as file:
                    json.dump(match_ids, file)
        except:
            with open(os.path.join(DATA_LOCATION, 'first_class_match_ids.json'), 'w') as file:
                    json.dump(match_ids, file)
    else:
        with open(os.path.join(DATA_LOCATION, 'first_class_match_ids.json'), 'r') as file:
            match_ids = json.load(file)
    logger.info("Creating player map for all matches grabbed")
    players = generate_player_match_dict(match_ids)

    logger.info("Done!")
    return players

if __name__ == "__main__":
    seasons  = []
    for year in range(2000, 2023):
        seasons.append(str(year))
        seasons.append(f"{str(year)}/{str((year%2000)+1).zfill(2)}")

    players_2000_onwards = create_player_first_class_matches_dict(seasons, skip_gather_ids=True)