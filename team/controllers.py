from flask_restplus import Resource
from . import models, validations, team_marshmallow
from flask_jwt_extended import jwt_required, get_jwt_identity
from player.models import Player
from flask import make_response, jsonify, request
from config import db
from user.models import User
from user.user_marshmallow import UserSchema
from auth.permissions import account_activation_required
from .api_model import pick_squad_model, team_api, manage_team_model, transfer_model, fantasy_cards_model
from werkzeug.exceptions import BadRequest
from player.marshmallow import PlayerSchema
from compeition.models import Competition


@team_api.route('/pick-squad')
class PickSquad(Resource):
    @team_api.expect(pick_squad_model)
    @jwt_required
    @account_activation_required
    def post(self):
        args = team_api.payload
        picks = args.get('squad')
        captain_id = int(args.get('captain-id'))
        if validations.validate_squad(picks, captain_id):
            email = get_jwt_identity()['email']
            user_obj = User.query.filter_by(email=email).first()
            user_squad = user_obj.squad.all()
            if len(user_squad) == 0:
                players_name = [player['name'] for player in picks]
                players_id = [player['id'] for player in picks]
                players_obj = Player.query.filter(
                    db.and_(Player.id.in_(players_id), Player.name.in_(players_name))).all()

                validations.validate_players(players_obj)

                picked_players_budget = sum(player.price for player in players_obj)
                validations.validate_budget(user_obj.budget, picked_players_budget)
                user_obj.budget -= picked_players_budget
                user_obj.squad_name = args.get('squad-name')
                user_obj.captain = captain_id

                for player in picks:
                    squad_obj = models.User_Player(
                        user_id=user_obj.id,
                        player_id=player['id'],
                        lineup=player['lineup']
                    )
                    db.session.add(squad_obj)
                fantasy_cards = models.Fantasy_cards(user_id=user_obj.id)
                db.session.add(fantasy_cards)
                db.session.commit()
                response = make_response(jsonify({"detail": "your team was successfully registered"}), 201)
                return response
            else:
                raise BadRequest(description="your team is complete!!")

@team_api.route('/my-team')
class ManageTeam(Resource):
    @jwt_required
    @account_activation_required
    def get(self):
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        user_response = UserSchema(only={'username', 'budget', 'overall_point', 'squad_name'})
        user_response = user_response.dump(user_obj)
        response = user_response
        response['captain-id'] = user_obj.captain
        lineup = user_obj.squad.filter_by(lineup=True).all()
        bench = user_obj.squad.filter_by(lineup=False).all()
        if len(lineup) == 11 and len(bench) == 4:
            lineup_result = []
            for element in lineup:
                player = Player.query.filter_by(id=element.player_id).first()
                lineup_result.append(player)
            bench_result = []
            for element in bench:
                player = Player.query.filter_by(id=element.player_id).first()
                bench_result.append(player)
            lineup_response = PlayerSchema(many=True)
            lineup_response = lineup_response.dump(lineup_result)
            for player in lineup_response:
                player['lineup'] = True
            bench_response = PlayerSchema(many=True)
            bench_response = bench_response.dump(bench_result)
            for player in bench_response:
                player['lineup'] = False
            squad = lineup_response + bench_response
            response['squad'] = squad
            user_cards = models.Fantasy_cards.query.filter_by(user_id=user_obj.id).first()
            cards_response = team_marshmallow.CardsSchema()
            cards_response = cards_response.dump(user_cards)
            response['cards'] = cards_response
            response = make_response(jsonify(response), 200)
            return response
        raise BadRequest(description="first pick your team")

    @team_api.expect(manage_team_model)
    @jwt_required
    @account_activation_required
    def put(self):
        args = team_api.payload
        captain_id = int(args.get('captain-id'))
        new_user_squad = sorted(args.get('squad'), key=lambda k: k['id'])
        if validations.validate_squad(new_user_squad, captain_id):
            email = get_jwt_identity()['email']
            user_obj = User.query.filter_by(email=email).first()
            user_squad = user_obj.squad.order_by(models.User_Player.player_id).all()

            players_name = [player['name'] for player in new_user_squad]
            players_id = [player['id'] for player in new_user_squad]
            players_obj = Player.query.filter(db.and_(Player.id.in_(players_id), Player.name.in_(players_name))).all()

            validations.validate_players(players_obj)
            for i in range(15):
                if players_id[i] == user_squad[i].player_id:
                    user_squad[i].lineup = new_user_squad[i]['lineup']
                else:
                    raise BadRequest(description="Your selected players do not exist in squad")

            user_obj.captain = captain_id
            db.session.commit()
            response = make_response(jsonify({"detail": "successfully upgraded"}), 200)
            return response


@team_api.route('/my-team/transfer')
class Transfer(Resource):
    @team_api.expect(transfer_model)
    @jwt_required
    @account_activation_required
    def post(self):
        args = team_api.payload
        player_in = Player.query.filter(db.and_(Player.name == args.get('player_in')['name'],
                                                Player.id == args.get('player_in')['id'])).first()
        player_out = Player.query.filter(db.and_(Player.name == args.get('player_out')['name'],
                                                 Player.id == args.get('player_out')['id'])).first()
        validations.validate_transfer_player(player_in, player_out)
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        user_squad = user_obj.squad.all()

        if len(user_squad) != 15:
            raise BadRequest(description="You cannot transfer player")

        user_squad_player_id = [player.player_id for player in user_squad]
        if (player_in.id not in user_squad_player_id) or (player_out.id in user_squad_player_id):
            raise BadRequest(description="You cannot transfer player")

        if user_obj.budget + (player_in.price - player_out.price) < 0:
            raise BadRequest(description="your budget is not enough")
        user_obj.budget += player_in.price - player_out.price

        squad_obj = user_squad[user_squad_player_id.index(player_in.id)]
        squad_obj.player_id = player_out.id

        db.session.commit()
        response = make_response(jsonify({"detail": "successfully upgraded"}), 200)
        return response


@team_api.route('/my-team/fantasy-cards')
class FantasyCards(Resource):
    @team_api.expect(fantasy_cards_model)
    @jwt_required
    @account_activation_required
    def post(self):
        email = get_jwt_identity()['email']
        args = team_api.payload
        user_obj = User.query.filter_by(email=email).first()
        cards = models.Fantasy_cards.query.filter_by(user_id=user_obj.id).first()
        if cards is None:
            raise BadRequest(description="first pick your squad")
        selected_card = str(args.get('card'))
        mode = str(args.get('mode'))
        if mode == 'active':
            card_number = validations.validate_cards_active(cards, selected_card)
            if card_number == 1:
                cards.bench_boost = 1
            elif card_number == 2:
                cards.free_hit = 1
            elif card_number == 3:
                cards.triple_captain = 1
            elif card_number == 4:
                cards.wild_card = 1
            db.session.commit()
            response = make_response(jsonify({"detail": "Successfully activated"}), 200)
            return response

        elif mode == 'cancel':
            card_number = validations.validate_cards_cancel(cards, selected_card)
            if card_number == 1:
                cards.bench_boost = 0
            elif card_number == 2:
                cards.free_hit = 0
            elif card_number == 3:
                cards.triple_captain = 0
            elif cards.wild_card == 4:
                cards.wild_card = 0
            db.session.commit()
            response = make_response(jsonify({"detail": "Successfully canceled"}), 200)
            return response
        else:
            raise BadRequest()
