from player.models import Player
from config import db
from .globals import player_max_price, player_min_price
import math


def update_all_player_price():
    all_players_sorted_by_point = Player.query.order_by(Player.point.desc()).all()
    max_point = all_players_sorted_by_point[0].point
    min_point = all_players_sorted_by_point[-1].point
    for i, player in enumerate(all_players_sorted_by_point):
        player.price = float(math.ceil((((player.point - min_point) / (max_point - min_point)) * (
                    player_max_price - player_min_price)) + player_min_price))
        if i % 250 == 0:
            db.session.commit()
    db.session.commit()
    print("All prices are updated")
