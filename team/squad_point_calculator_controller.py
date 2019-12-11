from flask_restplus import Resource
from config import db
from .models import squad, squadMatch
from match.models import MatchPlayer, Match


class CalculateSquadPointPerMatch(Resource):
    def get(self):
        all_squads = squad.query.all()

        for squad_ in all_squads:
            all_matches = Match.query.filter(db.and_(Match.competition_id == squad.competition_id, Match.status == 'FINNISHED', Match.lastUpdated > squad.created)).all()
            for match in all_matches:
                squad_point = 0
                for player in squad_.players:
                    match_player = MatchPlayer.query.filter(db.and_(MatchPlayer.player_id == player.id, MatchPlayer.match_id == match.id)).first()
                    if match_player:
                        squad_point += match_player.player_score
                to_insert = squadMatch(match_id = match.id, squad_id = squad.id, point = squad_point)
                db.session.add(to_insert)
            db.session.commit()


class CalculateSquadPointOverall(Resource):
    def get(self):
        
        all_squads = squad.query.all()
        for squadd in all_squads:
            all_squad_matches = squadMatch.query.filter(squadMatch.squad_id == squadd.id).all()
            squad_overall_point = 0
            for squad_match in all_squad_matches:
                squad_overall_point += squad_match.point
            squadd.point = squad_overall_point
        db.session.commit()
