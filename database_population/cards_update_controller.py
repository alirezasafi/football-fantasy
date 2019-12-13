from flask_restplus import Resource
from team.models import squad, CardsType, CardsCategory
from .api_model import database_population_update_api
from user.permissions import admin_required
from flask_jwt_extended import jwt_required
from player.models import Player
from config import db


@database_population_update_api.route('/card-update')
class UpdateCards(Resource):
    @jwt_required
    @admin_required
    def get(self):
        all_squads = squad.query.all()
        for squad_obj in all_squads:
            cards = squad_obj.cards
            for card in CardsCategory.score_cards.value:
                if cards.__getattribute__(card) == 1:
                    self.update_score(card, squad_obj)
                    cards.__setattr__(card, -1)
                    print("squad {} applied.".format(squad_obj.id))
                    break
            for card in CardsCategory.transfer_cards.value:
                if cards.__getattribute__(card) == 1:
                    cards.__setattr__(card, -1)

        db.session.commit()
        return {'message': 'All cards got updated.'}, 200

    def update_score(self, card, squad_obj):
        if card == CardsType.bench_boost.value:
            bench = squad_obj.players.filter_by(lineup=False).all()
            bench = [p.player_id for p in bench]
            players = Player.query.filter(Player.id.in_(bench)).all()
            for player in players:
                squad_obj.point += player.point

        elif card == CardsType.triple_captain.value:
            captain = Player.query.filter_by(id=squad_obj.captain).first()
            squad_obj.point += captain.point

