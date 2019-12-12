

available_competitions = [
    # 2000,2001,
    2002,2003,2013,2014,2015,2016,2017,2018,2019,2021
]

football_api={
    "Areas":"https://api.football-data.org/v2/areas",
    "CompetitionClub":"https://api.football-data.org/v2/competitions/%s/teams",#gets competition id 
    "MatchEvent":"https://data-ui.football-data.org/fd/competitions/%s/matches",#gets competition id 
    "Player":"https://api.football-data.org/v2/teams/%s"#gets club id
}


rules = {
    "upToSixtyMinutes": 1,
    "moreThanSixtyMinutes": 2,
    "DefGKGoal": 6,
    "MidGoal": 5,
    "FWGoal": 4,
    "yellowCard": -1,
    "redCard": -3,
    "assist": 3,
    "ownGoal": -2,
    "cleanSheet": 4,
    "AdditionalTransfer": 5
}