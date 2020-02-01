

available_competitions = [
    #2017,#porteghal
    #2015, #france
    #2013, #brazil
    #2003, #nethelands
    2002,2014,2019,2021
]

football_api={
    "Area":"https://api.football-data.org/v2/areas",
    "CompetitionClub":"https://api.football-data.org/v2/competitions/%s/teams",#gets competition id
    "MatchEvent":"https://data-ui.football-data.org/fd/competitions/%s/matches",#gets competition id
    "Player":"https://api.football-data.org/v2/teams/%s"#gets club id
}

player_max_price = 12
player_min_price = 3

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