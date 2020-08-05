from flask import send_file, current_app
from flask_restplus import Resource
from .api_model import player_api
from flask_jwt_extended import jwt_required
from compeition.models import Competition
from .player_marshmallow import PlayerSchema


@player_api.route('/media/<path:path>')
class MediaPlayer(Resource):
    def get(self, path):
        if not path.endswith('.png'):
            return {"message": "not found"}, 404

        img_path = current_app.config['MEDIA_ROOT'] + '/' + path
        try:
            return send_file(img_path, mimetype='image/png')
        except FileNotFoundError:
            img_path = current_app.config['MEDIA_ROOT'] + '/default.png'
            return send_file(img_path, mimetype='image/png')


@player_api.route('/<int:competition_id>/pick-squad')
class CompetitionPlayers(Resource):
    @jwt_required
    # @account_activation_required
    def get(self,competition_id):
        """get all players for a competition """
        competition = Competition.query.filter(Competition.id==competition_id).first()
        if competition == None:
            return {'message':'no competition found with given id'}, 404

        clubs = competition.clubs
        players = []
        for club in clubs:
            players+= club.players.all()

        players_response = PlayerSchema(many=True)
        players_response = players_response.dump(players)
        return players_response, 200
