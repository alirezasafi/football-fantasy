from . import (
    models
)
from flask import send_file, current_app, make_response, jsonify
from flask_restplus import Resource
from config import db
from .api_model import player_api
from auth.permissions import account_activation_required
from flask_jwt_extended import jwt_required
from compeition.models import Competition
from .marshmallow import PlayerSchema


@player_api.route('/media/player/<path:path>')
class MediaPlayer(Resource):
    def get(self, path):
        if path.endswith('.jpg'):
            img_path = current_app.config['MEDIA_ROOT'] + "/player/" + path
            try:
                return send_file(img_path, mimetype='image/jpg')
            except FileNotFoundError:
                response = make_response(jsonify({"detail": "404 NOT FOUND"}), 404)
                return response
        response = make_response(jsonify({"detail": "400 BAD REQUEST"}), 400)
        return response

@player_api.route('/<int:competition_id>/pick-squad')
class CompetitionPlayers(Resource):
    @jwt_required
    @account_activation_required
    def get(self,competition_id):
        """get all players for a competition """
        competition = Competition.query.filter(Competition.id==competition_id).first()
        if competition == None:
            return {'message':'no competition found with given id'}

        clubs = competition.clubs
        players = []
        for club in clubs:
            players+= club.players.all()

        players_response = PlayerSchema(many=True)
        players_response = players_response.dump(players)
        return players_response, 200
