from flask_restplus import Resource
from . import models, team_marshmallow
from compeition import permissions
from flask_jwt_extended import jwt_required, get_jwt_identity
from player.models import Player
from flask import make_response, jsonify
from config import db
from auth.permissions import account_activation_required
from .api_model import pick_squad_model, team_api, manage_team_model, transfer_model, fantasy_cards_model
from werkzeug.exceptions import BadRequest
from player.player_marshmallow import PlayerSchema
from user.user_marshmallow import UserSchema
from marshmallow import ValidationError
from functools import wraps


def get_squad_or_400(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_schema = UserSchema()
        user = user_schema.load(data=get_jwt_identity())
        competition_id = kwargs['competition_id']
        squad_obj = models.squad.query.filter(
            db.and_(models.squad.user_id == user.id, models.squad.competition_id == competition_id)).first()
        if not squad_obj:
            raise BadRequest(description="first pick your team")
        kwargs['squad'] = squad_obj
        kwargs['user'] = user
        return f(*args, **kwargs)
    return decorated_function


@team_api.route('/<int:competition_id>/pick-squad', endpoint="pick-squad")
class PickSquad(Resource):
    @team_api.expect(pick_squad_model)
    @jwt_required
    @account_activation_required
    @permissions.has_competition
    def post(self, competition_id):
        """available competitions are : Bundesliga: 2002, Eredivisie: 2003, Série A: 2013, Primera Division: 2014,
        Ligue 1: 2015, Championship: 2016, Primeira Liga: 2017, European Championship: 2018, Serie A: 2019,
        Premier League: 2021 """

        user_schema = UserSchema()
        user = user_schema.load(data=get_jwt_identity())

        args = team_api.payload
        squad_schema = team_marshmallow.SquadSchema()
        if squad_schema.has_squad(competition_id, user.id):
            raise BadRequest(description="your team is complete!!")
        errors = squad_schema.validate(data=args)
        if len(errors) != 0:
            raise BadRequest(description=errors)
        squad_object = squad_schema.load_object(data=args, partial=False, competition_id=competition_id,
                                                user_id=user.id)
        db.session.add(squad_object)

        squad_player_schema = team_marshmallow.squad_playerSchema()
        squad_player_objects = squad_player_schema.save_objects(squad_players=args['squad'], squad=squad_object,
                                                                partial=False)
        cards = models.Fantasy_cards(squad=squad_object)
        db.session.add(cards)
        db.session.add_all(squad_player_objects)
        db.session.commit()
        response = make_response(jsonify({"detail": "your team was successfully registered"}), 201)
        return response


@team_api.route('/<int:competition_id>/my-team', endpoint="manage_team")
class ManageTeam(Resource):
    @jwt_required
    @account_activation_required
    @permissions.has_competition
    def get(self, competition_id):
        user_schema = UserSchema()
        user = user_schema.load(data=get_jwt_identity())
        squad = models.squad.query.filter(
            db.and_(models.squad.user_id == user.id, models.squad.competition_id == competition_id)).first()
        if not squad:
            raise BadRequest(description="first pick your team")

        response_data = {'username': user.username}
        squad_schema = team_marshmallow.SquadSchema()
        squad_player_schema = team_marshmallow.squad_playerSchema(many=True, only={'player_id'})
        response_data.update(squad_schema.dump(squad))
        lineup = squad.players.filter_by(lineup=True).all()
        lineup = squad_player_schema.dump(lineup)
        bench = squad.players.filter_by(lineup=False).all()
        bench = squad_player_schema.dump(bench)
        lineup = Player.query.filter(Player.id.in_(lineup)).all()
        bench = Player.query.filter(Player.id.in_(bench)).all()
        player_schema = PlayerSchema(many=True)
        response_data['squad'] = player_schema.dump_players(lineup, True) + player_schema.dump_players(bench, False)
        card_schema = team_marshmallow.CardSchema()
        response_data['cards'] = card_schema.dump(squad.cards)
        response = make_response(response_data, 200)
        return response

    @team_api.expect(manage_team_model)
    @jwt_required
    @account_activation_required
    @permissions.has_competition
    def put(self, competition_id):
        user_schema = UserSchema()
        user = user_schema.load(data=get_jwt_identity())

        squad = models.squad.query.filter(
            db.and_(models.squad.user_id == user.id, models.squad.competition_id == competition_id)).first()
        if not squad:
            raise BadRequest(description="first pick your team")

        args = team_api.payload
        squad_schema = team_marshmallow.SquadSchema(partial=True)
        errors = squad_schema.validate(data=args)
        if len(errors) != 0:
            raise BadRequest(description=errors)

        squad_player_schema = team_marshmallow.squad_playerSchema()
        new_squad_players = sorted(args.get('squad'), key=lambda k: k['id'])
        squad_players = squad.players.order_by(models.squad_player.player_id).all()
        squad_player_schema.save_objects(new_squad_players=new_squad_players, partial=True, squad_players=squad_players)
        squad.captain = args.get('captain')
        db.session.commit()
        response = make_response(jsonify({"detail": "successfully upgraded"}), 200)
        return response


@team_api.route('/<int:competition_id>/my-team/transfer')
class Transfer(Resource):
    @team_api.expect(transfer_model)
    @jwt_required
    @account_activation_required
    @permissions.has_competition
    def post(self, competition_id):
        args = team_api.payload
        if 'player_in' not in args.keys() or 'player_out' not in args.keys():
            raise BadRequest(description="BAD REQUEST")
        user_schema = UserSchema()
        user = user_schema.load(data=get_jwt_identity())

        squad = models.squad.query.filter(
            db.and_(models.squad.user_id == user.id, models.squad.competition_id == competition_id)).first()
        if not squad:
            raise BadRequest(description="first pick your team")

        player_out = args.get('player_out')
        player_in = args.get('player_in')
        player_in_obj = Player.query.filter(db.and_(Player.name == player_in['name'],Player.id == player_in['id'])).first()
        player_out_obj = Player.query.filter(db.and_(Player.name == player_out['name'], Player.id == player_out['id'])).first()
        player_out = squad.players.filter_by(player_id=player_out['id']).first()

        if not player_out or not player_out_obj or not player_in_obj:
            raise BadRequest(description="BAD REQUEST")
        if player_out_obj.position != player_in_obj.position:
            raise BadRequest(description="You cannot transfer players with different position!!")

        if squad.players.filter_by(player_id=player_in['id']).first():

            raise BadRequest(description="this player is in your team.")

        if squad.budget + (player_out_obj.price - player_in_obj.price) < 0:
            raise BadRequest(description="your budget is not enough")
        self.apply_rules(squad)
        squad.budget += player_out_obj.price - player_in_obj.price
        player_out.player_id = player_in_obj.id

        db.session.commit()
        response = make_response(jsonify({"detail": "successfully upgraded"}), 200)
        return response

    def apply_rules(self, squad):
        cards = squad.cards
        from database_population.globals import rules
        if cards.wild_card == 1:  # active
            return
        elif squad.free_transfer is True or squad.free_transfer is None:
            squad.free_transfer = False
        elif squad.free_transfer is False:
            if squad.point - rules['AdditionalTransfer'] < 0:
                raise BadRequest("points not enough.")
            squad.point -= rules['AdditionalTransfer']


@team_api.route('/<int:competition_id>/my-team/cards', endpoint="cards")
class FantasyCards(Resource):
    @jwt_required
    @account_activation_required
    @permissions.has_competition
    def get(self, competition_id):
        user_schema = UserSchema()
        user = user_schema.load(data=get_jwt_identity())
        squad = models.squad.query.filter(
            db.and_(models.squad.user_id == user.id, models.squad.competition_id == competition_id)).first()

        if not squad:
            raise BadRequest(description="first pick your team")
        card_schema = team_marshmallow.CardSchema()
        response = card_schema.dump(squad.cards)
        return make_response(response, 200)

    @team_api.expect(fantasy_cards_model)
    @jwt_required
    @account_activation_required
    @permissions.has_competition
    def post(self, competition_id):
        args = team_api.payload
        cards_schema = team_marshmallow.CardSchema()
        try:
            cards_schema.load(args)
        except ValidationError as error:
            return error.messages
        user_schema = UserSchema()
        user = user_schema.load(data=get_jwt_identity())
        squad = models.squad.query.filter(
            db.and_(models.squad.user_id == user.id, models.squad.competition_id == competition_id)).first()
        if not squad:
            raise BadRequest(description="first pick your team")

        cards = squad.cards
        card = str(args.get('card'))
        mode = str(args.get('mode'))
        if mode == 'active':
            cards_schema.active_permission(cards, card)
            cards.__setattr__(card, 1)
            db.session.commit()
            response = make_response(jsonify({"detail": "Successfully activated."}), 200)
            return response

        if mode == 'inactive':
            cards_schema.inactive_permission(cards, card)
            cards.__setattr__(card, 0)
            db.session.commit()
            response = make_response(jsonify({"detail": "Successfully inactivated."}), 200)
            return response



from compeition.models import club_competition
@team_api.route("/<int:competition_id>/leaderboard")
class LeaderBoard(Resource):
    def get(self, competition_id):
        squads = models.squad.query.filter(models.squad.competition_id == competition_id).order_by(models.squad.point.desc()).all()
        output = team_marshmallow.LeaderBoard(many = True).dump(squads)
        return{'squads':output}