from flask_restplus import Resource
from . import models, parsers
from flask_jwt_extended import jwt_required, get_jwt_identity
from player.models import Player
from flask import make_response, jsonify, request
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
                if not validate_formation(picks):
                    response = make_response(jsonify({"detail": "formation validate error"}), 400)
                    return response
                user_obj.squad_name = args['squad-name']
                user_obj.captain = args['captain-id']

                for player in picks:
                    squad_obj = models.Squad(
                        user_id=user_obj.id,
                        player_id=player['player_id'],
                        lineup=player['lineup']
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


def validate_formation(squad):
    lineup_len = 0
    bench_len = 0
    for player in squad:
        if player['lineup']:
            lineup_len += 1
        else:
            bench_len += 1
    if lineup_len == 11 and bench_len == 4:
        return True
    return False


class ManageTeam(Resource):
    @jwt_required
    @account_actication_required
    def get(self):
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        lineup = user_obj.squad.filter_by(lineup=True).all()
        bench = user_obj.squad.filter_by(lineup=False).all()

        if len(lineup) == 11 and len(bench) == 4:
            squad = serialize_player(lineup, True)
            squad += serialize_player(bench, False)
            response = make_response(jsonify(squad), 200)
            return response
        response = make_response(jsonify({"detail": "first pick your team!!"}), 400)
        return response

    @api.expect(parsers.ManageTeam_parser)
    @jwt_required
    @account_actication_required
    def put(self):
        args = parsers.ManageTeam_parser.parse_args()
        new_user_squad = sorted(args['squad'], key=lambda k: k['player_id'])
        if validate_squad(new_user_squad):
            email = get_jwt_identity()['email']
            user_obj = User.query.filter_by(email=email).first()
            user_squad = user_obj.squad.order_by(models.Squad.player_id).all()
            for i in range(15):
                if new_user_squad[i]['player_id'] == user_squad[i].player_id:
                    user_squad[i].lineup = new_user_squad[i]['lineup']
                else:
                    response = make_response(jsonify({"detail": "400 BAD REQUEST"}), 400)
                    return response

            user_obj.captain = args['captain-id']
            db.session.commit()
            response = make_response(jsonify({"detail": "successfully upgraded"}), 200)
            return response
        else:
            response = make_response(jsonify({"detail": "400 BAD REQUEST"}), 400)
            return response


def validate_squad(squad):
    GP = 0
    DF = 0
    MF = 0
    FD = 0
    for player in squad:
        if player['position'] == 'Goalkeeper':
            GP += 1
        elif player['position'] == 'Defender':
            DF += 1
        elif player['position'] == 'Midfielder':
            MF += 1
        else:
            FD += 1
    if not (GP == 2 and DF == 5 and MF == 5 and FD == 3):
        return False
    GP = 0
    DF = 0
    MF = 0
    FD = 0
    formations = [(4,3,3), (4,4,2), (4,5,1), (3,4,3), (3,5,2), (5,4,1)]
    lineup = 0
    for player in squad:
        if player['position'] == 'Goalkeeper' and player['lineup']:
            GP += 1
            lineup += 1
        elif player['position'] == 'Defender' and player['lineup']:
            DF += 1
            lineup += 1
        elif player['position'] == 'Midfielder' and player['lineup']:
            MF += 1
            lineup += 1
        elif player['position'] == 'Forward' and player['lineup']:
            FD += 1
            lineup += 1
    print((DF,MF,FD))
    if (DF,MF,FD) in formations and GP == 1 and lineup == 11:
        return True
    else:
        return False


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
