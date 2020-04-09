from config import ma
from marshmallow import Schema, fields
from player.player_marshmallow import PlayerSchema
from club.club_marshmallow import ClubSchema
from game_event.marshmallow import EventSchema
from match.match_marshmallow import MatchSchema, Match_PlayerSchema
from club.models import Club
from match.models import Match, MatchPlayer, Status
from config import db
from game_event.models import Event, EventImage


class Match_player_detail_Schema(Match_PlayerSchema):
    utcDate = fields.Method('get_utcDate')
    match_result = fields.Method('get_match_result')
    opponent = fields.Method('get_opponent')

    def get_match_result(self, obj):
        result = {'awayTeamScore': obj.match.awayTeamScore, 'homeTeamScore': obj.match.homeTeamScore}
        return result

    def get_utcDate(self, obj):
        return str(obj.match.utcDate)

    def get_opponent(self, obj):
        opponent = {}
        if obj.home_away.value == "Home":
            opponent_obj = Club.query.filter_by(id=obj.match.awayTeam_id).first()
            opponent['name'] = opponent_obj.name
            opponent['image'] = opponent_obj.image
            return opponent
        opponent_obj = Club.query.filter_by(id=obj.match.homeTeam_id).first()
        opponent['name'] = opponent_obj.name
        opponent['image'] = opponent_obj.image
        return opponent


class CustomEventSchema(EventSchema):
    event_opponent = fields.Method('get_opponent')
    image = fields.Method('get_image')

    def get_image(self, obj):
        return EventImage.__getattr__(obj.event_type.name).value

    def get_opponent(self, obj):
        homeTeam_name = obj.match.homeTeam.name
        awayTeam_name = obj.match.awayTeam.name
        player_club_name = obj.player.club.name
        if str(homeTeam_name) == str(player_club_name):
            return awayTeam_name
        return homeTeam_name


class PlayerStatisticsSchema(Schema):
    player = ma.Nested(PlayerSchema(exclude={'club', 'matches', 'events'}))
    club = ma.Nested(ClubSchema(exclude={'lastUpdated'}))
    matches = ma.Nested(Match_player_detail_Schema(exclude={'player', 'lastUpdated'}), many=True)
    events = ma.Nested(CustomEventSchema(exclude={'player'}), many=True)


class Squad_playerStatistics(PlayerSchema):
    statistic = fields.Method('get_statistic')

    def get_statistic(self, obj):
        statistic = {'this_week':
                         {'score': 0, 'minutes_played': 0, 'Goal': 0, 'OwnGoal': 0, 'Assist': 0, 'YellowCard': 0,
                          'YellowRedCard': 0, 'RedCard': 0, 'PlayingStatus': None, 'utcDate': None},

                     'last_5_weeks':
                         {'score': 0, 'minutes_played': 0, 'Goal': 0, 'OwnGoal': 0, 'Assist': 0, 'YellowCard': 0,
                          'YellowRedCard': 0, 'RedCard': 0, 'playing_percentage': 0}}
        club = obj.club
        matches = Match.query.filter(db.and_(
            db.or_(Match.awayTeam_id == club.id, Match.homeTeam_id == club.id), Match.status == Status.FINISHED.name)). \
            order_by(Match.utcDate.desc()).limit(5).all()
        matches_id = [match.id for match in matches]
        matches_player = obj.matches.filter(MatchPlayer.match_id.in_(matches_id))
        matches_player = sorted(matches_player, key=lambda M: M.match.utcDate, reverse=True)

        if not matches_player:
            return statistic

        statistic['this_week']['score'] = matches_player[0].player_score
        statistic['this_week']['minutes_played'] = matches_player[0].minutes_played
        statistic['this_week']['utcDate'] = str(matches[0].utcDate)
        statistic['this_week']['PlayingStatus'] = matches_player[0].playerPlayingStatus.value
        events = obj.events.filter(Event.match_id.in_(matches_id)).all()

        for match in matches_player:
            statistic['last_5_weeks']['score'] += int(match.player_score)
            statistic['last_5_weeks']['minutes_played'] += int(match.minutes_played)

        for event in events:
            if event.match_id == matches_id[0]:
                statistic['this_week'][event.event_type.value] += 1
            statistic['last_5_weeks'][event.event_type.value] += 1
        statistic['last_5_weeks']['playing_percentage'] = (statistic['last_5_weeks']['minutes_played'] / (5*90)) * 100
        return statistic
