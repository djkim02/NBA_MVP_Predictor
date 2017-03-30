from bs4 import BeautifulSoup
import requests
import cPickle as pickle
from nba_py import player
from nba_py.player import get_player
from nba_py.player import PlayerGeneralSplits
import json

# Returns the top 40 scoring leaders of a season.
# if year = 2000, this function returns the top 40 scoring leaders of 1999-00 season
# if year = 2017, this function returns the top 40 scoring leaders of 2016-17 season
def get_scoring_leaders(year):
	# Parsing the names from ESPN
	link = "http://www.espn.com/nba/statistics/player/_/stat/scoring-per-game/sort/avgPoints/year/" + str(year)
	html_response = requests.get(link)
	beautiful_soup_html = BeautifulSoup(html_response.text, "html.parser")

	players = [a.string for a in beautiful_soup_html.findAll('a')]
	scoring_leaders = []

	# Index of where the first player starts
	START = 21
	# 
	SKIP = 16

	# Fetching top 40 scoring leader's names
	for i in range(4):
		for j in range(10):
			index = START + j
			scoring_leaders.append(players[index])
		START += SKIP

	return scoring_leaders

# Saves a dictionary of top 40 scoring leaders from 1999-00 season through 2016-17 season to a pickle
def save_scoring_leaders_in_a_pickle(scoring_leaders_pkl_fn):
	season_scoring_leaders_dict = {}
	for i in range(2000, 2018):
		season_scoring_leaders_dict[i] = get_scoring_leaders(i)

	pickle.dump(season_scoring_leaders_dict, open(scoring_leaders_pkl_fn, 'wb'))

# Returns a dictionary of top 40 scoring leaders from 1999-00 season through 2016-17 season to a pickle
def read_scoring_leaders_from_a_pickle(scoring_leaders_pkl_fn):
	top40_scorers = pickle.load(open(scoring_leaders_pkl_fn, 'rb'))
	return top40_scorers

# Returns first and last name given a full name
def parse_first_and_last_name(name):
	first_and_last_name = player.split(' ', 1)
	first_name = first_and_last_name[0]
	last_name = first_and_last_name[1]
	return first_name, last_name

# Given a season (one integer) returns a formatted season
# ex) if season = 2000, returns "1999-00"
# 	  if season = 2017, returns "2016-17"
def format_season(season):
	return str(season-1) + "-" + str(season)[2:]


# Returns the statistics of a player in a season
def get_stats(first_name, last_name, season):
	formatted_season = format_season(season)
	player_id = get_player(first_name, last_name, season=formatted_season)
	stats = PlayerGeneralSplits(player_id, season=formatted_season)
	return json.dumps(stats.json)



if __name__ == "__main__":
	scoring_leaders_pkl_fn = 'scoring_leaders.pkl'
	scoring_leaders = read_scoring_leaders_from_a_pickle(scoring_leaders_pkl_fn)
	seasons = scoring_leaders.keys()

	for season in seasons:
		for player in scoring_leaders[season]:
			first_name, last_name = parse_first_and_last_name(player)
			stats = get_stats(first_name, last_name, season)
			break
		break