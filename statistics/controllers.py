from .api_model import statistics_api
from flask_restplus import Resource
from .statistics_marshmallow import PlayerStatisticsSchema, Squad_playerStatistics
from config import db
from game_event.models import Event
from match.models import Match, MatchPlayer, Status
from flask_jwt_extended import jwt_required
from auth.permissions import account_activation_required
from compeition.permissions import has_competition
from team.controllers import get_squad_or_400
from team.team_marshmallow import squad_playerSchema
from player.models import Player


@statistics_api.route('/player/<int:player_id>', endpoint='player_statistic')
class PlayerStatistics(Resource):
    def get(self, player_id):
        player = Player.query.filter_by(id=player_id).first()
        if not player:
            return {"message": "player not found!!"}, 404
        club = player.club
        matches = Match.query.filter(db.and_(
            db.or_(Match.awayTeam_id == club.id, Match.homeTeam_id == club.id), Match.status == Status.FINISHED.name)).\
            order_by(Match.utcDate.desc()).limit(5).all()
        matches_id = [match.id for match in matches]

        matches_player = player.matches.filter(MatchPlayer.match_id.in_(matches_id))
        matches_player = sorted(matches_player, key=lambda M: M.match.utcDate, reverse=True)
        events = player.events.filter(Event.match_id.in_(matches_id)).all()
        schema = PlayerStatisticsSchema()
        response = schema.dump({'player': player, 'club': club, 'matches': matches_player, 'events': events})
        return response, 200


@statistics_api.route('/squad/<int:competition_id>')
class SquadStatistics(Resource):
    @jwt_required
    @account_activation_required
    @has_competition
    @get_squad_or_400
    def get(self, competition_id, **kwargs):
        squad = kwargs['squad']
        squad_player = squad.players.all()
        squad_player_schema = squad_playerSchema(only={'player_id'}, many=True)
        players_id = squad_player_schema.dump(squad_player)
        players = Player.query.filter(Player.id.in_(players_id))
        sps_schema = Squad_playerStatistics(only={'id', 'name', 'price', 'position', 'image', 'statistic'}, many=True)
        response = {'squad': sps_schema.dump(players)}
        return response, 200
