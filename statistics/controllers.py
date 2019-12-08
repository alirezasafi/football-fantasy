from .api_model import statistics_api
from flask_restplus import Resource
from .statistics_marshmallow import PlayerStatisticsSchema
from player.models import Player
from config import db
from game_event.models import Event
from match.models import Match, MatchPlayer, Status


@statistics_api.route('/player/<int:player_id>')
class PlayerStatistics(Resource):
    def get(self, player_id):
        player = Player.query.filter_by(id=player_id).first()
        if not player:
            return {"message": "player not found!!"}, 404
        club = player.club
        matches = Match.query.filter(db.and_(
            db.or_(Match.awayTeam == club.id, Match.homeTeam == club.id), Match.status == Status.FINISHED.name)).\
            order_by(Match.utcDate.desc()).limit(5).all()
        matches_id = [match.id for match in matches]

        matches_player = player.matches.filter(MatchPlayer.match_id.in_(matches_id))
        matches_player = sorted(matches_player, key=lambda M: M.match.utcDate, reverse=True)
        events = player.events.filter(Event.match_id.in_(matches_id)).all()

        # matches_player = player.matches.all()
        # matches = [m_player.match for m_player in matches_player]
        # recently_matches = sorted(matches, key=lambda D: D.utcDate, reverse=True)[:5]
        # recently_matches_player = sorted(matches_player, key=lambda M: M.match.utcDate, reverse=True)[:5]
        # print(player.events.filter(Event.match_id.in_(matches_id)).all())

        schema = PlayerStatisticsSchema()
        response = schema.dump({'player': player, 'club': club, 'matches': matches_player, 'events': events})
        return response, 200
