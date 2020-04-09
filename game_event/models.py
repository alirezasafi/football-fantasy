from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM
from match.models import MatchPlayer
from player.models import Player
from match.models import Match
from database_population.calculate_event_point import calculate_event_point
from database_population.globals import rules

class EventType(enum.Enum):
    GO = 'Goal'
    OWNGO = 'OwnGoal'
    AS = 'Assist'
    YELLOW_CARD = 'YellowCard'
    YELLOW_RED_CARD = 'YellowRedCard'
    RED_CARD = 'RedCard'

class EventImage(enum.Enum):
    GO = 'https://c7.uihere.com/files/187/994/415/goal-football-clip-art-hand-painted-football-goals.jpg'
    OWNGO = 'https://mpng.pngfly.com/20180208/wvw/kisspng-football-goal-clip-art-flaming-dragon-cliparts-5a7cad6892f820.297351721518120296602.jpg'
    AS = 'https://cdn2.iconfinder.com/data/icons/sports-v2/512/Football.png'
    YELLOW_CARD = 'https://images.vexels.com/media/users/3/146861/isolated/preview/dcafb4e33c5514e9b53b3d929501feaf-football-yellow-card-icon-by-vexels.png'
    YELLOW_RED_CARD = 'https://cdn1.iconfinder.com/data/icons/soccer-flat/64/soccer-18-512.png'
    RED_CARD = 'https://images.vexels.com/media/users/3/146857/isolated/preview/d55e89657228964a776f7dab3c0537ca-football-red-card-icon-by-vexels.png'

class MatchSubstitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_in_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    player_out_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    minute = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey(Match.id))

@db.event.listens_for(MatchSubstitution, 'before_insert')
def player_score_update_after_substitution(mapper, connection, target):
    player_in = target.player_in_id
    player_out = target.player_out_id
    player_out_minutes_played = target.minute
    player_in_minutes_played = 90 - player_out_minutes_played

    match_player_in = MatchPlayer.query.filter(db.and_(MatchPlayer.player_id == target.player_in_id, MatchPlayer.match_id == target.match_id)).first()
    match_player_out = MatchPlayer.query.filter(db.and_(MatchPlayer.player_id == target.player_out_id, MatchPlayer.match_id == target.match_id)).first()

    player_in_score = match_player_in.player_score
    player_out_score = match_player_out.player_score
    if player_in_minutes_played < 60 and player_in_minutes_played > 1:
        player_in_score += rules['upToSixtyMinutes']
    elif player_in_minutes_played >= 60:
        player_in_score += rules['moreThanSixtyMinutes']
    
    if player_out_minutes_played < 60 and player_out_minutes_played > 1:
        player_out_score += (rules['upToSixtyMinutes'] - rules['moreThanSixtyMinutes'])

    connection.execute(
        MatchPlayer.__table__.
        update().        
        values(player_score=player_in_score, minutes_played = player_in_minutes_played).
        where(MatchPlayer.player_id == player_in))
    connection.execute(
        MatchPlayer.__table__.
        update().        
        values(player_score=player_out_score, minutes_played = player_out_minutes_played).
        where(MatchPlayer.player_id == player_out))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    event_type = db.Column(ENUM(EventType, name="event_type"))
    minute = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey(Match.id))

@db.event.listens_for(Event, 'after_insert')
def event_update_after_match_update(mapper, connection, target):
    match_player = MatchPlayer.query.filter(db.and_(MatchPlayer.player_id == target.player_id, MatchPlayer.match_id == target.match_id)).first()
    event_point = calculate_event_point(target, match_player)
    player_score = match_player.player_score + event_point

    connection.execute(
        MatchPlayer.__table__.
        update().        
        values(player_score=player_score).
        where(MatchPlayer.player_id == target.player_id))
