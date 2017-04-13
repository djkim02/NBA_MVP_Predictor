from bs4 import BeautifulSoup
import requests
import cPickle as pickle
from nba_py import player
import json

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
HEADER = {'User-Agent': USER_AGENT}

# Returns the names of top 40 scoring leaders of a season from ESPN.
# if year = 2000, this function returns the top 40 scoring leaders of 1999-00 season
# if year = 2017, this function returns the top 40 scoring leaders of 2016-17 season
def get_scoring_leaders_from_espn(year):
	# Parsing the names from ESPN
	link = "http://www.espn.com/nba/statistics/player/_/stat/scoring-per-game/sort/avgPoints/year/" + str(year)
	html_response = requests.get(link, headers = HEADER)
	beautiful_soup_html = BeautifulSoup(html_response.text, "html.parser")

	players = [a.string for a in beautiful_soup_html.findAll('a')]
	scoring_leaders = []

	# Index of where the first player starts
	START = 21
	SKIP = 16

	# Fetching top 40 scoring leader's names
	for i in range(4):
		for j in range(10):
			index = START + j
			scoring_leaders.append(players[index])
		START += SKIP

	return scoring_leaders

# Returns a list of top 50 scoring leaders' player IDs, names, and teams for a given season from nba.com
def get_scoring_leaders_from_nba(year):
	link = "http://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={}&SeasonType=Regular+Season&StatCategory=PTS&Rank=N".format(format_season(year))
	print link
	response = requests.get(link, headers = HEADER)
	json_response_data = json.loads(response.text)
	full_player_list = json_response_data["resultSet"]["rowSet"][:50]

	player_list = []
	for each_player in full_player_list:
		player_data = []

		# Only storing PLAYER_ID, PLAYER, TEAM
		player_data.append(each_player[0])
		player_data.append(each_player[2])
		player_data.append(each_player[3])

		player_list.append(player_data)

	return player_list

def get_stats_of_top50_scorers_with_ranks(year):
	return

def get_stats_of_everyone_with_ranks(year):
	base_link = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight=".format(format_season(year))
	base_response = requests.get(base_link, headers = HEADER)
	base_json_response_data = json.loads(base_response.text)
	base_full_player_list = base_json_response_data["resultSets"][0]["rowSet"]

	advanced_link = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight=".format(format_season(year))
	advanced_response = requests.get(advanced_link, headers = HEADER)
	advanced_json_response_data = json.loads(advanced_response.text)
	advanced_full_player_list = advanced_json_response_data["resultSets"][0]["rowSet"]

	season_stats = {}
	for i in range(len(base_full_player_list)):
		base_player = base_full_player_list[i]
		player_stats = []
		player_stats.extend(base_player[0:2])
		player_stats.extend(base_player[5:10])
		player_stats.append(base_player[12])
		player_stats.append(base_player[15])
		player_stats.append(base_player[18])
		player_stats.extend(base_player[21:26])
		player_stats.extend(base_player[29:38])
		player_stats.append(base_player[40])
		player_stats.append(base_player[43])
		player_stats.append(base_player[46])
		player_stats.extend(base_player[49:54])
		player_stats.extend(base_player[57:61])
		advanced_player = advanced_full_player_list[i]
		player_stats.extend(advanced_player[10:14])
		player_stats.append(advanced_player[18])
		player_stats.extend(advanced_player[20:23])
		player_stats.append(advanced_player[24])
		player_stats.extend(advanced_player[35:39])
		player_stats.append(advanced_player[43])
		player_stats.extend(advanced_player[45:48])
		player_stats.append(advanced_player[49])
		season_stats[base_player[0]] = player_stats

	return season_stats


# Uses data parsed from stats.nba.com to get season statistics of top 50 scorers from 1996-97 season to 2016-17 season
def get_stats_from_top_50_scorers_and_pickle():
	stats_dict = {}

	for season in range(1997, 2018):
		formatted_season = format_season(season)
		print "Starting to parse {} season's stats".format(formatted_season)
		# Fetching a list of top 50 scorers' player ID, name, and team
		all_players_stats = []
		players = get_scoring_leaders_from_nba(season)

		for each_player in players:
			print "Parsing {}".format(each_player[1])
			player_general_splits = player.PlayerGeneralSplits(each_player[0], season=formatted_season)
			player_stats = each_player
			player_stats.extend(player_general_splits.json["resultSets"][0]["rowSet"][0][1:30])

			# ID, name, team, season, GP, W, L, W_PCT, MIN, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, FTM, FTA, FT_PCT, OREB, DREB, REB, AST, TOV, STL, BLK, BLKA, PF, PFD, PTS, PLUS_MINUS, DD2, TD3
			all_players_stats.append(player_stats)

		stats_dict[season] = all_players_stats

		print "Done with parsing {} season's stats".format(formatted_season)

	stats_fn = "top_50_scorers_from_1996-97_to_2016-17.pkl"
	pickle.dump(stats_dict, open(stats_fn, 'wb'))
	return stats_dict

# Returns all players who played in a season
def get_all_players_from_a_season(year):
	formatted_season = format_season(year)
	return player.PlayerList(season=formatted_season)

# Saves a dictionary of top 40 scoring leaders from 1999-00 season through 2016-17 season to a pickle
def save_scoring_leaders_in_a_pickle(scoring_leaders_pkl_fn):
	season_scoring_leaders_dict = {}
	for i in range(2000, 2018):
		season_scoring_leaders_dict[i] = get_scoring_leaders_from_espn(i)

	pickle.dump(season_scoring_leaders_dict, open(scoring_leaders_pkl_fn, 'wb'))

# Returns a dictionary of top 40 scoring leaders from 1999-00 season through 2016-17 season to a pickle
def read_scoring_leaders_from_a_pickle(scoring_leaders_pkl_fn):
	top40_scorers = pickle.load(open(scoring_leaders_pkl_fn, 'rb'))
	return top40_scorers

# Returns first and last name given a full name
def parse_first_and_last_name(player):
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
def get_stats(name, first_name, last_name, season):
	formatted_season = format_season(season)
	if name == "Yao Ming":
		player_id = player.get_player(name, season=formatted_season)
	else:
		player_id = player.get_player(first_name, last_name, season=formatted_season)

	player_general_splits = player.PlayerGeneralSplits(player_id, season=formatted_season)
	stats = []
	stats.append(name)
	stats.extend(player_general_splits.json["resultSets"][0]["rowSet"][0][1:30])
	return stats

def get_stats_with_id(player_id, season):
	formatted_season = format_season(season)
	player_general_splits = player.PlayerGeneralSplits(player_id, season=formatted_season)
	stats = []
	stats.append(name)
	stats.extend(player_general_splits.json["resultSets"][0]["rowSet"][0][1:30])
	return stats

# GROUP_VALUE, GP, W, L, W_PCT, MIN, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, FTM, FTA, FT_PCT, OREB, DREB, REB, AST, TOV, STL, BLK, BLKA, PF, PFD, PTS, PLUS_MINUS, DD2, TD3
def get_all_stats_and_pickle():
	scoring_leaders_pkl_fn = 'scoring_leaders.pkl'
	scoring_leaders = read_scoring_leaders_from_a_pickle(scoring_leaders_pkl_fn)
	seasons = scoring_leaders.keys()
	stats_dict = {}
	for season in seasons:
		season_stats = []
		print "Starting to parse {} season's stats".format(format_season(season))

		for player in scoring_leaders[season]:
			print "Parsing {}".format(player)
			first_name, last_name = parse_first_and_last_name(player)
			stats = get_stats(player, first_name, last_name, season)
			season_stats.append(stats)

		stats_dict[season] = season_stats
		print "Done with parsing {} season's stats".format(format_season(season))

	all_stats_fn = "all_stats.pkl"
	pickle.dump(stats_dict, open(all_stats_fn, 'wb'))

if __name__ == "__main__":
	# players = get_scoring_leaders_from_nba(2017)
	print get_stats_of_everyone_with_ranks(2017)

	# Russell Westbrook
	# print players[0][1]
	# print json.dumps(player.PlayerGeneralSplits(players[0][0], measure_type='Advanced').json)

	# # James Harden
	# print players[1][1]
	# print player.PlayerDefenseTracking(players[1][0]).json["resultSets"][0]["rowSet"][0]

	# # Isaiah Thomas
	# print players[2][1]
	# print player.PlayerDefenseTracking(players[2][0]).json["resultSets"][0]["rowSet"][0]

	# # Anthony Davis
	# print players[3][1]
	# print player.PlayerDefenseTracking(players[3][0]).json["resultSets"][0]["rowSet"][0]

	# # Kawhi Leonard
	# print players[8][1]
	# print player.PlayerDefenseTracking(players[8][0]).json["resultSets"][0]["rowSet"][0]

	# # Lebron James
	# print players[7][1]
	# print player.PlayerDefenseTracking(players[7][0]).json["resultSets"][0]["rowSet"][0]
