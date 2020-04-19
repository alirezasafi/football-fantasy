from config import ma, db
from . import models
from marshmallow import fields, Schema, validates_schema, post_dump, INCLUDE, validates
from werkzeug.exceptions import BadRequest
from player.models import Player
from .models import CardStatus, CardsType, CardsCategory
from user.user_marshmallow import UserSchema
from compeition.competition_marshmallow import CompetitionSchema
from player.player_marshmallow import PlayerEventSchema


class squad_playerSchema(Schema):
    name = fields.String(required=True)
    id = fields.Integer(required=True)
    position = fields.String(required=True)
    lineup = fields.Boolean(required=True)
    player_id = fields.Integer(dump_only=True)

    class Meta:
        unknown = INCLUDE

    @post_dump
    def dump_id(self, data, **kwargs):
        return data['player_id']

    def save_objects(self, squad_players, **kwargs):
        if kwargs['partial'] is False:
            squad_obj = kwargs['squad']
            objects = []
            for player in squad_players:
                squad_player_obj = models.squad_player(
                    squad=squad_obj,
                    player_id=player['id'],
                    lineup=player['lineup']
                )
                objects.append(squad_player_obj)
            return objects
        else:
            new_squad_players = kwargs['new_squad_players']
            for i in range(15):
                if squad_players[i].player_id == new_squad_players[i]['id']:
                    squad_players[i].lineup = new_squad_players[i]['lineup']
                else:
                    raise BadRequest(description="BAD REQUEST")


class SquadSchema(Schema):
    name = fields.String(required=True)
    favourite_team = fields.String()
    budget = fields.Float(required=True)
    captain = fields.Integer(required=True)
    squad = fields.Nested(squad_playerSchema, many=True)

    class Meta:
        unknown = INCLUDE

    def has_squad(self, competition_id, user_id):
        squad = models.squad.query.filter(
            db.and_(models.squad.competition_id == competition_id, models.squad.user_id == user_id)) .first()
        if squad:
            return True
        return False

    def load_object(self, data, **kwargs):
        if kwargs['partial'] is False:
            squad_obj = models.squad(competition_id=kwargs['competition_id'],
                                     user_id=kwargs['user_id'],
                                     budget=data['budget'],
                                     captain=data['captain'],
                                     name=data['name'])
            return squad_obj

    @validates_schema(skip_on_field_errors=False)
    def validate_fields(self, data, **kwargs):
        if kwargs.get("partial") is False:
            if not data.__contains__('name'):
                raise BadRequest(description="please specify the name of your squad.")
            if not data.__contains__('captain'):
                raise BadRequest(description="the captain has not been selected.")
            if not data.__contains__('squad'):
                raise BadRequest(description="your squad is incomplete.")
            if data.get("squad").__contains__({}):
                raise BadRequest(description="your squad is incomplete.")

    @validates_schema
    def validate_squad(self, data, **kwargs):
        squad = data['squad']
        captain = data['captain']
        formations = [(4, 3, 3), (4, 4, 2), (4, 5, 1), (3, 4, 3), (3, 5, 2), (5, 4, 1), (5, 2, 3), (5, 3, 2)]
        position = [player['position'] for player in squad]
        lineup = [player['lineup'] for player in squad]
        if not (position.count('Goalkeeper') == 2 and position.count('Defender') == 5
                and position.count('Midfielder') == 5 and position.count('Forward') == 3):
            raise BadRequest(description="select a squad with 15 players, consisting of: 2 Goalkeepers, 5 Defenders, "
                                         "5 Midfielders, 3 Forwards")

        captain_status = [player['lineup'] for player in squad if player['id'] == captain]
        if len(captain_status) != 1 or captain_status[0] is False:
            raise BadRequest(description="Your selected captain must be in lineup!!")

        squad_formation = {'Goalkeeper': 0, 'Defender': 0, 'Midfielder': 0, 'Forward': 0}
        for i in range(len(squad)):
            if lineup[i] is True:
                squad_formation[position[i]] += 1
        if (lineup.count(True) != 11
                or ((squad_formation['Defender'], squad_formation['Midfielder'], squad_formation['Forward']) not in formations)
                or squad_formation['Goalkeeper'] != 1):
            raise BadRequest(description="select your lineup players providing that 1 goalkeeper, at least 3 "
                                         "defenders and at least 1 forward. ")
        self.validate_players_and_budget(data, **kwargs)

    def validate_players_and_budget(self, data, **kwargs):
        squad = data['squad']
        squad_name = [player['name'] for player in squad]
        squad_id = [player['id'] for player in squad]
        players_obj = Player.query.filter(
                    db.and_(Player.id.in_(squad_id), Player.name.in_(squad_name))).all()
        if len(players_obj) != 15:
            raise BadRequest(description="Your selected players do not exist!!")
        positions = [player.position.value for player in players_obj]
        if not (positions.count('Goalkeeper') == 2 and positions.count('Defender') == 5
                and positions.count('Midfielder') == 5 and positions.count('Attacker') == 3):
            raise BadRequest(description="select a squad with 15 players, consisting of: 2 Goalkeepers, 5 Defenders, "
                                         "5 Midfielders, 3 Forwards")

        players_club = [player.club for player in players_obj]
        for club in players_club:
            if players_club.count(club) >= 4:
                raise BadRequest(description="You can select up to 3 players from a single club!!")
        if kwargs['partial'] is False:
            picked_players_price = sum(player.price for player in players_obj)
            budget = data['budget']
            if int(picked_players_price) not in range(0, 101) or int(budget) not in range(0, 101):
                raise BadRequest(description="Your budget is not enough!!")

        # for club in players_club:
        # clubs_obj = Club.query.filter(Club.id.in_(players_club)).all()
        # print(clubs_obj)


class CardSchema(Schema):
    card = fields.String(required=True, load_only=True)
    mode = fields.String(required=True, load_only=True)
    bench_boost = fields.Method('get_bench_boost', dump_only=True)
    free_hit = fields.Method('get_free_hit', dump_only=True)
    triple_captain = fields.Method('get_triple_captain', dump_only=True)
    wild_card = fields.Method('get_wild_card', dump_only=True)

    @validates("mode")
    def validate_mode(self, value):
        if value != CardStatus.active.name and value != CardStatus.inactive.name:
            raise BadRequest("BAD REQUEST (mode)!!")

    @validates("card")
    def validate_card(self, value):
        if value not in CardsType.__members__.keys():
            raise BadRequest("BAD REQUEST (card)!!")

    def get_bench_boost(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.bench_boost]

    def get_free_hit(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.free_hit]

    def get_triple_captain(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.triple_captain]

    def get_wild_card(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.wild_card]

    def active_permission(self, cards, to_active):
        if cards.__getattribute__(to_active) == -1:
            raise BadRequest("you used this card")

        cards_status = [cards.bench_boost, cards.free_hit, cards.triple_captain, cards.wild_card]
        if cards_status.count(1) != 0:
            raise BadRequest("Only one card can be activated in a single Gameweek.")

    def inactive_permission(self, cards, to_inactive):
        if to_inactive in CardsCategory.transfer_cards.value:
            raise BadRequest("failed to inactive.")
        if cards.__getattribute__(to_inactive) == -1:
            raise BadRequest("you used this card")


class LeaderBoard(ma.ModelSchema):
    class Meta:
        model = models.squad
        fields = (
            'name',
            'competition',
            'user',
            'point',
        )
    user = ma.Nested(UserSchema())
    competition = ma.Nested(CompetitionSchema())
