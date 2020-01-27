from flask_restplus import Resource
from match.models import Match, MatchPlayer
from game_event.models import Event, MatchSubstitution
from player.models import Player
from .api_model import database_population_update_api
from config import db
import datetime
from .globals import rules, player_max_price, player_min_price
import math


@database_population_update_api.route('/player-score-calculate')
class PlayerScoreCalc(Resource):
    def get(self):

        """ calculate the player score for every match based on events and matches"""
        all_matches = Match.query.filter(Match.status == 'FINISHED').all()
        match_counter = 1
        for match in all_matches:
            # get all players played in that match
            matchplayers = [matchplayer for matchplayer in MatchPlayer.query.filter(
                MatchPlayer.match_id == match.id).all()]
            players = [matchplayer.player for matchplayer in matchplayers]
            for matchplayer in matchplayers:
                if matchplayer.lastUpdated > match.lastUpdated:
                    break
                match_score = 0
                events = Event.query.filter(
                    db.and_(Event.match_id == match.id, Event.player_id == matchplayer.player.id)).all()
                substitution = MatchSubstitution.query.filter(db.and_(db.or_(
                    MatchSubstitution.player_in_id == matchplayer.player.id, MatchSubstitution.player_out_id == matchplayer.player.id), MatchSubstitution.match_id == match.id)).first()
                # calculating minutes played
                minutes_played = 0
                if substitution == None:
                    if matchplayer.playerPlayingStatus.name == 'LN':
                        minutes_played = 90
                else:
                    in_out = None

                    if substitution.player_in_id == matchplayer.player.id:
                        minutes_played = 90 - int(substitution.minute)
                    else:
                        minutes_played = int(substitution.minute)
                if minutes_played == 0:
                    continue
                # adding minutes_played to player
                matchplayer.minutes_played = minutes_played
                # score calculating by minutes
                if minutes_played < 60 and minutes_played > 1:
                    match_score += rules['upToSixtyMinutes']
                elif minutes_played >= 60:
                    match_score += rules['moreThanSixtyMinutes']
                # calculating player events
                for event in events:
                    if event.event_type.name == 'YELLOW_CARD':
                        match_score -= rules['yellowCard']
                    elif event.event_type.name == 'RED_CARD' or event.event_type.name == 'YELLOW_RED_CARD':
                        match_score -= rules['redCard']
                    elif event.event_type.name == 'GO':
                        if matchplayer.player.position.name == 'Goalkeeper' or matchplayer.player.position.name == 'Defender':
                            match_score += rules['DefGKGoal']
                        elif matchplayer.player.position.name == 'Midfielder':
                            match_score += rules['MidGoal']
                        else:
                            match_score += rules['FWGoal']
                    elif event.event_type.name == 'AS':
                        match_score += rules['assist']
                    elif event.event_type.name == 'OWNGO':
                        match_score += rules['ownGoal']
                # if the player postition was not set
                if matchplayer.player.position == None:
                    matchplayer.player_score = 0
                    matchplayer.lastUpdated = datetime.datetime.utcnow()
                    break
                # calculating goalkeeper and defender clean sheet
                elif matchplayer.player.position.name == 'Goalkeeper' or matchplayer.player.position.name == 'Defender':
                    if matchplayer.home_away.name == 'HOME':
                        if matchplayer.match.awayTeamScore == 0:
                            match_score += rules['cleanSheet']
                    else:
                        if matchplayer.match.homeTeamScore == 0:
                            match_score += rules['cleanSheet']
                #adding match_score to player
                matchplayer.player_score = match_score
                matchplayer.lastUpdated = datetime.datetime.utcnow()
            # commit changes after 50 matches
            if match_counter % 50 == 0:
                db.session.commit()
            print(str(match_counter)+" out of "+str(len(all_matches))+ " matches")

            match_counter+=1
        db.session.commit()
        return {'message':'player scores for all matches got updated.'}


@database_population_update_api.route('/player-overall-point')
class PlayerOverallPointCalc(Resource):
    def get(self):
        """calculate and update sum of the match points and prices for every player if needed"""
        all_players = Player.query.all()
        player_counter = 1
        for player in all_players:
            matches = MatchPlayer.query.filter(MatchPlayer.player_id == player.id).all()
            player_point = player.point
            for match in matches:
                # if update is not needed break
                if player.lastUpdated > match.lastUpdated or match.player_score == None:
                    break
                player_point += match.player_score
            
            if len(matches):
                player.price = player_point/len(matches)
            player.point = player_point
            player.lastUpdated = datetime.datetime.utcnow()
            if player_counter % 250 == 0:
                db.session.commit()
                print(str(player_counter // 250) + " out of " + str(len(all_players)//250))
            player_counter += 1
            
        db.session.commit()
        all_players_sorted_by_point = Player.query.order_by(Player.point.desc()).all()
        max_point = all_players_sorted_by_point[0].point
        min_point = all_players_sorted_by_point[-1].point
        for player in all_players_sorted_by_point:
            matches = MatchPlayer.query.filter(MatchPlayer.player_id == player.id).all()   
            player.price = math.ceil((((player.point-min_point) / (max_point - min_point)) * (player_max_price - player_min_price)) + player_min_price)

        db.session.commit()

        return {'message':'All players scores got updated.'}