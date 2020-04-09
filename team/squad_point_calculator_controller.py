from flask_restplus import Resource
from config import db
from .models import squad, squadMatch
from match.models import MatchPlayer, Match
from .api_model import team_api

@team_api.route('/squad-point-calculator')
class CalculateSquadPoint(Resource):
    def get(self):
        """calculates squad point for every match that occured after squad creation and overall squad point"""
        all_squads = squad.query.all()
        # per match calculation
        for squad_ in all_squads:
            #get all matches that started after last time the squad point was modified
            all_matches = Match.query.filter(db.and_(Match.competition_id == squad_.competition_id, Match.status == 'FINNISHED', Match.utcDate > squad_.point_lastUpdated)).all()
            for match in all_matches:
                squad_point = 0
                for player in squad_.players:
                    # if the player was transfered after the match don't add his point
                    if player.joined_date > match.utcDate:
                        continue
                    match_player = MatchPlayer.query.filter(db.and_(MatchPlayer.player_id == player.id, MatchPlayer.match_id == match.id)).first()
                    #if the player was in the match add his point to the match score of the squad
                    if match_player:
                        squad_point += match_player.player_score
                #if the score is not 0 then insert it
                if squad_point != 0:
                    to_insert = squadMatch(match_id = match.id, squad_id = squad_.id, point = squad_point)
                    db.session.add(to_insert)
            db.session.commit()
        #overall calculation
        for squadd in all_squads:
            all_squad_matches = squadMatch.query.filter(squadMatch.squad_id == squadd.id).all()
            squad_overall_point = 0
            for squad_match in all_squad_matches:
                squad_overall_point += squad_match.point
            squadd.point = squad_overall_point
            db.session.commit()
        return {"message":"Squad points are calculated; permatch and overall"}