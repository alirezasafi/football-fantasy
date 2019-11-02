from werkzeug.exceptions import BadRequest
from . import exceptions


def validate_players(players_obj):
    if len(players_obj) != 15:
        raise BadRequest(description="Your selected players do not exist!!")
    players_club = [player.club for player in players_obj]
    for club in players_club:
        if players_club.count(club) >= 4:
            raise BadRequest(description="You can select up to 3 players from a single club!!")


def validate_budget(user_budget, picked_players_budget):
    if user_budget < picked_players_budget:
        raise BadRequest(description="Your budget is not enough!!")


def validate_squad(squad, captain_id):
    GK, DF, MF, FD = 0, 0, 0, 0
    for player in squad:
        if player['position'] == 'Goalkeeper':
            GK += 1
        elif player['position'] == 'Defender':
            DF += 1
        elif player['position'] == 'Midfielder':
            MF += 1
        elif player['position'] == 'Forward':
            FD += 1
    if not (GK == 2 and DF == 5 and MF == 5 and FD == 3):
        raise exceptions.SquadException()

    lineup_players = [player['player_id'] for player in squad if player['lineup']]
    if captain_id not in lineup_players:
        raise BadRequest(description="Your selected captain must be in lineup!!")

    GK, DF, MF, FD = 0, 0, 0, 0
    formations = [(4,3,3), (4,4,2), (4,5,1), (3,4,3), (3,5,2), (5,4,1)]
    lineup = 0
    for player in squad:
        if player['position'] == 'Goalkeeper' and player['lineup']:
            GK += 1
            lineup += 1
        elif player['position'] == 'Defender' and player['lineup']:
            DF += 1
            lineup += 1
        elif player['position'] == 'Midfielder' and player['lineup']:
            MF += 1
            lineup += 1
        elif player['position'] == 'Forward' and player['lineup']:
            FD += 1
            lineup += 1
    if (DF,MF,FD) in formations and GK == 1 and lineup == 11:
        return True
    else:
        raise exceptions.FormationException




