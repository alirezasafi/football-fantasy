from flask_restplus import Resource
from . import models, parsers
from flask_jwt_extended import jwt_required, get_jwt_identity
from player.models import Player
from flask import make_response, jsonify
from config import api, db
from user.models import User
from auth.permissions import account_actication_required


class PickSquad(Resource):
    @jwt_required
    @account_actication_required
    def get(self):
        players = Player.query.all()
        players_response = []
        for player in players:
            players_response.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "price": player.price,
                    "image": player.image,
                    "shirt_number": player.shirt_number,
                    "club": player.club,
                    "position": player.position.value,
                    "status": player.status
                }
            )
        response = make_response(jsonify(players_response), 200)
        return response

    @api.expect(parsers.PickSquad_parser)
    @jwt_required
    @account_actication_required
    def post(self):
        args = parsers.PickSquad_parser.parse_args()
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        picks = args['picks']
        squad = user_obj.squad.all()

        if len(squad) == 0:
            if len(picks) == 15:
                user_obj.squad_name = args['squad-name']
                for player in picks:
                    squad_obj = models.Squad(
                        user_id=user_obj.id,
                        player_id=player['player_id']
                    )
                    db.session.add(squad_obj)
                db.session.commit()
                response = make_response(jsonify({"detail": "your team was successfully registered"}), 201)
                return response
            else:
                response = make_response(jsonify({"detail": "you should pick 15 player"}), 400)
                return response
        else:
            response = make_response(jsonify({"detail": "your squad is complete"}), 400)
            return response
