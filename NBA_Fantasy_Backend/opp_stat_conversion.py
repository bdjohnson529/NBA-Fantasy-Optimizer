def convert_opp_stat(stat_name):

	abb_name = ""

	if(stat_name=="Opponent Offensive Rebounds per Game"):
		abb_name = "ORB"
	elif(stat_name=="Opponent Defensive Rebounds per Game"):
		abb_name = "DRB"
	elif(stat_name=="Opponent Points per Game"):
		abb_name = "PTS"
	elif(stat_name=="Opponent Assists per Game"):
		abb_name = "AST"
	elif(stat_name=="Opponent Turnovers per Game"):
		abb_name = "TOV"
	elif(stat_name=="Opponent Blocks per Game"):
		abb_name = "BLK"
	elif(stat_name=="Opponent Steals per Game"):
		abb_name = "STL"
	elif(stat_name=="Opponent Three Pointers Made per Game"):
		abb_name = "3P"

	return abb_name