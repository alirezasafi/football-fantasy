from flask_restplus import Resource
from . import models, validations
from flask_jwt_extended import jwt_required, get_jwt_identity
from player.models import Player
from flask import make_response, jsonify, request
from config import db
from user.models import User
from auth.permissions import account_actication_required
from .api_model import pick_squad_model, team_api, manage_team_model, transfer_model
from werkzeug.exceptions import BadRequest


@team_api.route('/pick-squad')
class PickSquad(Resource):
    @jwt_required
    @account_actication_required
    def get(self):
        players = Player.query.all()
        players_response = []
        for player in players:
            player_image = None
            if player.image is not None:
                player_image = request.host + '/media/player/' + player.image

            players_response.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "price": player.price,
                    "image": player_image,
                    "shirt_number": player.shirt_number,
                    "club": player.club,
                    "position": player.position.value,
                    "status": player.status.value
                }
            )
        response = make_response(jsonify(players_response), 200)
        return response

    @team_api.expect(pick_squad_model)
    @jwt_required
    @account_actication_required
    def post(self):
        args = team_api.payload
        picks = args.get('picks')
        captain_id = int(args.get('captain-id'))
        if validations.validate_squad(picks, captain_id):
            email = get_jwt_identity()['email']
            user_obj = User.query.filter_by(email=email).first()
            user_squad = user_obj.squad.all()
            if len(user_squad) == 0:
                players_name = [player['name'] for player in picks]
                players_id = [player['player_id'] for player in picks]
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
                        player_id=player['player_id'],
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
    @account_actication_required
    def get(self):
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        response = serializer_user(user_obj)
        lineup = user_obj.squad.filter_by(lineup=True).all()
        bench = user_obj.squad.filter_by(lineup=False).all()
        if len(lineup) == 11 and len(bench) == 4:
            squad = serialize_player(lineup, True)
            squad += serialize_player(bench, False)
            response['squad'] = squad
            response = make_response(jsonify(response), 200)
            return response
        return BadRequest(description="first pick your team")

    @team_api.expect(manage_team_model)
    @jwt_required
    @account_actication_required
    def put(self):
        args = team_api.payload
        captain_id = int(args.get('captain-id'))
        new_user_squad = sorted(args.get('squad'), key=lambda k: k['player_id'])
        if validations.validate_squad(new_user_squad, captain_id):
            email = get_jwt_identity()['email']
            user_obj = User.query.filter_by(email=email).first()
            user_squad = user_obj.squad.order_by(models.User_Player.player_id).all()

            players_name = [player['name'] for player in new_user_squad]
            players_id = [player['player_id'] for player in new_user_squad]
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
    @account_actication_required
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


def serialize_player(squad, in_lineup):
    result = []
    for element in squad:
        player = Player.query.filter_by(id=element.player_id).first()
        player_image = None
        if player.image is not None:
            player_image = request.host + '/media/player/' + player.image
        result.append(
            {
                "id": player.id,
                "name": player.name,
                "price": player.price,
                "image": player_image,
                "shirt_number": player.shirt_number,
                "club": player.club,
                "position": player.position.value,
                "status": player.status.value,
                "lineup": in_lineup
            }
        )
    return result


def serializer_user(user_obj):
    user_response = {'username': user_obj.username, 'squad_name': user_obj.squad_name, 'captain': user_obj.captain,
                     'budget': user_obj.budget, 'overall_point': user_obj.overall_point}
    return user_response