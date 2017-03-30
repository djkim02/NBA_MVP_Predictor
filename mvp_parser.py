from bs4 import BeautifulSoup
import requests
import cPickle as pickle
from nba_py import player
from nba_py.player import get_player

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


def parse_first_and_last_name(name):


# Returns the statistics of a player in a season
def get_stats(name, season):
	return


if __name__ == "__main__":
	scoring_leaders_pkl_fn = 'scoring_leaders.pkl'
	scoring_leaders = read_scoring_leaders_from_a_pickle(scoring_leaders_pkl_fn)
	print scoring_leaders