from bs4 import BeautifulSoup
import requests
import cPickle as pickle
from nba_py import player
import json

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
HEADER = {'User-Agent': USER_AGENT}
MVP_DICT = {
	1997:"Karl Malone",			# PF
	1998:"Michael Jordan",		# SG
	1999:"Karl Malone",			# PF
	2000:"Shaquille O'Neal",	# C
	2001:"Allen Iverson",		# PG
	2002:"Tim Duncan",			# PF
	2003:"Tim Duncan",			# PF
	2004:"Kevin Garnett",		# PF
	2005:"Steve Nash",			# PG
	2006:"Steve Nash",			# PG
	2007:"Dirk Nowitzki",		# PF
	2008:"Kobe Bryant",			# SG
	2009:"LeBron James",		# SF
	2010:"LeBron James",		# SF
	2011:"Derrick Rose",		# PG
	2012:"LeBron James",		# SF
	2013:"LeBron James",		# SF
	2014:"Kevin Durant",		# SF
	2015:"Stephen Curry",		# PG
	2016:"Stephen Curry"		# PG
	# 6 PGs, 2 SGs, 5 SFs, 6 PFs, 1 C
	# 6 PGs, 7 Swingmans, 7 Bigmans
}

NUM_QUALIFYING_PLAYERS_DICT = {
	1997: 441,
	1998: 439,
	1999: 440,
	2000: 439,
	2001: 441,
	2002: 440,
	2003: 428,
	2004: 442,
	2005: 464,
	2006: 458,
	2007: 458,
	2008: 451,
	2009: 445,
	2010: 442,
	2011: 452,
	2012: 478,
	2013: 469,
	2014: 482,
	2015: 492,
	2016: 476,
	2017: 486
}

CATEGORY_DICT = {
	# 0:"POSITION",
	# 1:"PLAYER_NAME",
	# 2:"GP",
	# 3:"W",
	# 4:"W_PCT",
	# 5:"MIN",
	# 6:"FG_PCT",
	# 7:"FG3_PCT",
	# 8:"FT_PCT",
	# 9:"REB",
	# 10:"AST",
	# 11:"TOV",
	# 12:"STL",
	# 13:"BLK",
	# 14:"PTS",
	# 15:"PLUS_MINUS",
	# 16:"DD2",
	# 17:"TD3",
	18:["GP_RANK", 50, 100, 150, False],
	19:["W_RANK", 25, 50, 75, False],
	20:["L_RANK", 25, 50, 75, False],
	21:["W_PCT_RANK", 25, 50, 75, False],
	22:["MIN_RANK", 25, 50, 75, False],
	23:["FG_PCT_RANK", 50, 100, 150, True],
	24:["FG3_PCT_RANK", 25, 50, 75, True],
	25:["FT_PCT_RANK", 50, 100, 150, True],
	26:["REB_RANK", 25, 50, 75, True],
	27:["AST_RANK", 15, 30, 45, True],
	28:["TOV_RANK", 25, 50, 75, False],
	29:["STL_RANK", 25, 50, 75, True],
	30:["BLK_RANK", 25, 50, 75, True],
	31:["PTS_RANK", 15, 30, 45, True],
	32:["PLUS_MINUS_RANK", 15, 30, 45, True],
	33:["DD2_RANK", 25, 50, 75, True],
	34:["TD3_RANK", 5, 10, 15, False]
}

# Returns a list of top 50 scoring leaders' player IDs, names, and teams for a given season from nba.com
def get_scoring_leaders_from_nba(year):
	link = "http://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={}&SeasonType=Regular+Season&StatCategory=PTS&Rank=N".format(format_season(year))
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
	formatted_season = format_season(year)
	print "Starting to parse {} season's scoring leaders".format(formatted_season)
	scoring_leaders = get_scoring_leaders_from_nba(year)
	print "Done with parsing {} season's scoring leaders".format(formatted_season)
	print "Starting to parse {} season's stats".format(formatted_season)
	stats_everyone = get_stats_of_everyone_with_ranks(year)
	print "Done with parsing {} season's stats".format(formatted_season)
	print "Starting to filter the stats: top 50 scorers for {} season".format(formatted_season)
	top50_scorers_stats = []
	for scoring_leader in scoring_leaders:
		top50_scorers_stats.append(stats_everyone[scoring_leader[0]])
	print "Done with filtering the stats: top 50 scorers for {} season".format(formatted_season)
	return top50_scorers_stats


def get_stats_of_everyone_with_ranks(year):
	base_link = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=Starters&TeamID=0&VsConference=&VsDivision=&Weight=".format(format_season(year))
	base_response = requests.get(base_link, headers = HEADER)
	base_json_response_data = json.loads(base_response.text)
	base_full_player_list = base_json_response_data["resultSets"][0]["rowSet"]

	advanced_link = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=Starters&TeamID=0&VsConference=&VsDivision=&Weight=".format(format_season(year))
	advanced_response = requests.get(advanced_link, headers = HEADER)
	advanced_json_response_data = json.loads(advanced_response.text)
	advanced_full_player_list = advanced_json_response_data["resultSets"][0]["rowSet"]

	season_stats = {}
	for i in range(len(base_full_player_list)):
		base_player = base_full_player_list[i]
		player_stats = []
		player_stats.extend(base_player[0:2])
		player_stats.extend(base_player[5:7])
		player_stats.extend(base_player[8:10])
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
		player_stats.append(advanced_player[38])
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

	stats_fn = "all_stats.pkl"
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


# PLAYER_ID, PLAYER_NAME, GP, W, W_PCT, MIN, FG_PCT, FG3_PCT, FT_PCT, REB, AST, TOV, STL, BLK, PTS,
# PLUS_MINUS, DD2, TD3, GP_RANK, W_RANK, L_RANK, W_PCT_RANK, MIN_RANK, FG_PCT_RANK, FG3_PCT_RANK, FT_PCT_RANK,
# REB_RANK, AST_RANK, TOV_RANK, STL_RANK, BLK_RANK, PTS_RANK, PLUS_MINUS_RANK, DD2_RANK, TD3_RANK
# OFF_RATING, DEF_RATING, NET_RATING, AST_PCT, REB_PCT, EFG_PCT, TS_PCT, USG_PCT, PIE, OFF_RATING_RANK
# DEF_RATING_RANK, NET_RATING_RANK, AST_PCT_RANK, REB_PCT_RANK, EFG_PCT_RANK, TS_PCT_RANK, USG_PCT_RANK, PIE_RANK
def get_all_base_stats_and_advanced_stats_and_pickle():
	stats_dict = {}
	for i in range(1997, 2018):
		stats_dict[i] = get_stats_of_top50_scorers_with_ranks(i)

	all_stats_fn = "all_stats.pkl"
	pickle.dump(stats_dict, open(all_stats_fn, 'wb'))


# 5 positions, PG, SG, SF, PF, C
def parse_five_position_from_wikipedia(first_name, last_name):
	name = first_name + "_" + last_name
	link = "https://en.wikipedia.org/wiki/" + name
	html_response = requests.get(link, headers = HEADER)
	beautiful_soup_html = BeautifulSoup(html_response.text, "html.parser")
	tags = [a.string for a in beautiful_soup_html.findAll('a', href=True)][:50]
	for tag in tags:
		if tag == "Point guard":
			print first_name + " " + last_name + " is a " + tag
			return 1
		elif tag == "Shooting guard":
			print first_name + " " + last_name + " is a " + tag
			return 2
		elif tag == "Small forward":
			print first_name + " " + last_name + " is a " + tag
			return 3
		elif tag == "Power forward":
			print first_name + " " + last_name + " is a " + tag
			return 4
		elif tag == "Center":
			print first_name + " " + last_name + " is a " + tag
			return 5

	link = "https://en.wikipedia.org/wiki/" + name + "_(basketball)"
	html_response = requests.get(link, headers = HEADER)
	beautiful_soup_html = BeautifulSoup(html_response.text, "html.parser")
	tags = [a.string for a in beautiful_soup_html.findAll('a', href=True)][:50]
	for tag in tags:
		if tag == "Point guard":
			print first_name + " " + last_name + " is a " + tag
			return 1
		elif tag == "Shooting guard":
			print first_name + " " + last_name + " is a " + tag
			return 2
		elif tag == "Small forward":
			print first_name + " " + last_name + " is a " + tag
			return 3
		elif tag == "Power forward":
			print first_name + " " + last_name + " is a " + tag
			return 4
		elif tag == "Center":
			print first_name + " " + last_name + " is a " + tag
			return 5
	print first_name + " " + last_name + "'s position could not be found!"
	return 0

# 3 positions, PG, Swingman, Bigman
def parse_three_position_from_wikipedia(first_name, last_name):
	name = first_name + "_" + last_name

	link = "https://en.wikipedia.org/wiki/" + name
	html_response = requests.get(link, headers = HEADER)
	beautiful_soup_html = BeautifulSoup(html_response.text, "html.parser")
	tags = [a.string for a in beautiful_soup_html.findAll('a', href=True)][:50]
	for tag in tags:
		if tag == "Point guard":
			print first_name + " " + last_name + " is a " + tag
			return 1
		elif tag == "Shooting guard" or tag == "Small forward":
			print first_name + " " + last_name + " is a " + tag
			return 2
		elif tag == "Power forward" or tag == "Center":
			print first_name + " " + last_name + " is a " + tag
			return 3

	link = "https://en.wikipedia.org/wiki/" + name + "_(basketball)"
	html_response = requests.get(link, headers = HEADER)
	beautiful_soup_html = BeautifulSoup(html_response.text, "html.parser")
	tags = [a.string for a in beautiful_soup_html.findAll('a', href=True)][:50]
	for tag in tags:
		if tag == "Point guard":
			print first_name + " " + last_name + " is a " + tag
			return 1
		elif tag == "Shooting guard" or tag == "Small forward":
			print first_name + " " + last_name + " is a " + tag
			return 2
		elif tag == "Power forward" or tag == "Center":
			print first_name + " " + last_name + " is a " + tag
			return 3

	print first_name + " " + last_name + "'s position could not be found!"
	return 0


def add_five_position_to_stats(all_stats):
	seasons = all_stats.keys()
	not_found_list_dict = {}
	for season in seasons:
		not_found_list = []
		print "Getting position of {} season".format(format_season(season))
		season_stats = all_stats[season]
		for player_stats in season_stats:
			first_name, last_name = parse_first_and_last_name(player_stats[1])
			pos = parse_five_position_from_wikipedia(first_name, last_name)
			if pos == 0:
				not_found_list.append(player_stats[1])
			else:
				player_stats[0] = pos
		not_found_list_dict[season] = not_found_list

	return not_found_list_dict


def add_three_position_to_stats(all_stats):
	seasons = all_stats.keys()
	not_found_list_dict = {}
	for season in seasons:
		not_found_list = []
		print "Getting position of {} season".format(format_season(season))
		season_stats = all_stats[season]
		for player_stats in season_stats:
			first_name, last_name = parse_first_and_last_name(player_stats[1])
			pos = parse_three_position_from_wikipedia(first_name, last_name)
			if pos == 0:
				not_found_list.append(player_stats[1])
			else:
				player_stats[0] = pos
		not_found_list_dict[season] = not_found_list

	return not_found_list_dict


# Given the category, calculates the model count of top 25,
# top 50, top 75, and below for a given season
def get_model_count_given_stats_and_category(all_stats, category, num_pos):
	seasons = all_stats.keys()
	top1 = CATEGORY_DICT[category][1]
	top2 = CATEGORY_DICT[category][2]
	top3 = CATEGORY_DICT[category][3]

	# [rank_given_pg_and_mvp, rank_given_swingman_and_mvp, rank_given_bigman_and_mvp,
	# rank_given_pg_and_not_mvp, rank_given_swingman_and_not_mvp, rank_given_bigman_and_not_mvp]
	category_given_position_and_mvp = []
	for i in range(0, num_pos * 2):
		outer = []
		for j in range(0, 4):
			outer.append(0)
		category_given_position_and_mvp.append(outer)

	for season in range(1997, 2017):
		# top25 = NUM_QUALIFYING_PLAYERS_DICT[season] / 16
		# top50 = NUM_QUALIFYING_PLAYERS_DICT[season] / 8
		# top75 = NUM_QUALIFYING_PLAYERS_DICT[season] / 4

		mvp_name = MVP_DICT[season]
		season_stats = all_stats[season]
		for player_stats in season_stats:
			offset = -1
			if player_stats[1] == mvp_name:
				offset = num_pos - 1

			if player_stats[category] < top1:
				category_given_position_and_mvp[player_stats[0] + offset][0] += 1
			elif player_stats[category] < top2:
				category_given_position_and_mvp[player_stats[0] + offset][1] += 1
			elif player_stats[category] < top3:
				category_given_position_and_mvp[player_stats[0] + offset][2] += 1
			else:
				category_given_position_and_mvp[player_stats[0] + offset][3] += 1

	return category_given_position_and_mvp


def get_number_of_qualifying_players(year):
	base_link = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=Starters&TeamID=0&VsConference=&VsDivision=&Weight=".format(format_season(year))
	base_response = requests.get(base_link, headers = HEADER)
	base_json_response_data = json.loads(base_response.text)
	base_full_player_list = base_json_response_data["resultSets"][0]["rowSet"]
	return len(base_full_player_list)


def get_number_of_qualifying_players_for_all_seasons():
	return_dict = {}
	for season in range(1997, 2018):
		return_dict[season] = get_number_of_qualifying_players(season)
	return return_dict


def add_three_positions_for_missing_players(all_stats):
	for season in range(1997, 2018):
		season_stats = all_stats[season]
		for player_stats in season_stats:
			name = player_stats[1]
			if name == "Reggie Jackson" or name == "Mike Conley" or name == "Mike James" or name == "Rodney Stuckey":
				player_stats[0] = 1
			elif name == "Eric Williams" or name == "Tracy Murray" or name == "Andrei Kirilenko" or name == "Hedo Turkoglu" or name == "Mike Miller" or name == "Mike Dunleavy":
				player_stats[0] = 2
			elif name == "Clifford Robinson" or name == "Larry Johnson" or "Lamar Odom":
				player_stats[0] = 3


def get_cpt_given_model_count_three_pos(model_count, given_position):
	model_count_given_not_mvp = model_count[0:3]
	model_count_given_mvp = model_count[3:]

	if given_position:
		total_given_mvp = [6.0, 7.0, 7.0]
		total_not_given_mvp = [192.0, 456.0, 332.0]

		for i in range(0, 3):
			for j in range(0, 4):
				model_count_given_mvp[i][j] /= total_given_mvp[i]
				model_count_given_not_mvp[i][j] /= total_not_given_mvp[i]

		posterior_mvp = model_count_given_mvp
		posterior_not_mvp = model_count_given_not_mvp

	else:
		posterior_mvp = [0, 0, 0, 0]
		posterior_not_mvp = [0, 0, 0, 0]
		total_mvp = 20.0
		total_not_mvp = 980.0

		for i in range(0, 3):
			for j in range(0, 4):
				posterior_mvp[j] += model_count_given_mvp[i][j]
				posterior_not_mvp[j] += model_count_given_not_mvp[i][j]

		for i in range(0, 4):
			posterior_mvp[i] /= total_mvp
			posterior_not_mvp[i] /= total_not_mvp

	return posterior_mvp, posterior_not_mvp

def discretize_player_stats_given_season(season_stats):
	discretized_stats = []
	for player_stats in season_stats:
		stats_dict = {}
		stats_dict["NAME"] = player_stats[1]
		stats_dict["Position"] = position_int_to_string(player_stats[0])
		for category in range(18, 35):
			category_name = CATEGORY_DICT[category][0]
			category_top1 = CATEGORY_DICT[category][1]
			category_top2 = CATEGORY_DICT[category][2]
			category_top3 = CATEGORY_DICT[category][3]

			if player_stats[category] < category_top1:
				stats_dict[category_name] = "top" + str(category_top1)
			elif player_stats[category] < category_top2:
				stats_dict[category_name] = "top" + str(category_top2)
			elif player_stats[category] < category_top3:
				stats_dict[category_name] = "top" + str(category_top3)
			else:
				stats_dict[category_name] = "other"
		discretized_stats.append(stats_dict)

	return json.dumps(discretized_stats)

def position_int_to_string(position):
	if position == 1:
		return "PG"
	elif position == 2:
		return "Swingman"
	elif position == 3:
		return "Bigman"
	else:
		return "INVALID POSITION"

def json_to_file(json_stats, file_name):
	json_file = open(file_name, 'w')
	json_file.write(json_stats)


if __name__ == "__main__":
	all_stats_with_three_pos_fn = "all_stats_with_three_pos.pkl"
	all_stats = pickle.load(open(all_stats_with_three_pos_fn, 'rb'))
	# category = 22
	# given_position = CATEGORY_DICT[category][4]
	# posterior = get_cpt_given_model_count_three_pos(get_model_count_given_stats_and_category(all_stats, category, 3), given_position)

	# for cpt in posterior:
	# 	for category in cpt:
	# 		print category
	for season in all_stats.keys():
		json_to_file(discretize_player_stats_given_season(all_stats[season]), "{}.json".format(season))
