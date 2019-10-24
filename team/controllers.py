from flask_restplus import Resource
from . import models, exceptions
from flask_jwt_extended import jwt_required, get_jwt_identity
from player.models import Player
from flask import make_response, jsonify, request
from config import db
from user.models import User
from auth.permissions import account_actication_required
from .api_model import pick_squad_model, team_api, manage_team_model

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
        picks = args['picks']

        if validate_squad(picks):
            email = get_jwt_identity()['email']
            user_obj = User.query.filter_by(email=email).first()
            user_squad = user_obj.squad.all()
            if len(user_squad) == 0:
                user_obj.squad_name = args['squad-name']
                user_obj.captain = args['captain-id']
                user_obj.budget = args['budget']
                for player in picks:
                    squad_obj = models.User_Player(
                        user_id=user_obj.id,
                        player_id=player['player_id'],
                        lineup=player['lineup']
                    )
                    db.session.add(squad_obj)
                db.session.commit()
                response = make_response(jsonify({"detail": "your team was successfully registered"}), 201)
                return response


@team_api.route('/my-team')
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

    @team_api.expect(manage_team_model)
    @jwt_required
    @account_actication_required
    def put(self):
        args = team_api.payload
        new_user_squad = sorted(args['squad'], key=lambda k: k['player_id'])
        if validate_squad(new_user_squad):
            email = get_jwt_identity()['email']
            user_obj = User.query.filter_by(email=email).first()
            user_squad = user_obj.squad.order_by(models.User_Player.player_id).all()
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
        raise exceptions.SquadException()
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
    if (DF,MF,FD) in formations and GP == 1 and lineup == 11:
        return True
    else:
        raise exceptions.FormationException


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
