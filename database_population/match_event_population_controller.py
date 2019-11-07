import requests
from flask_restplus import Resource
from .api_model import database_population_api
from .database_decorators import database_empty_required
from config import db
from flask import current_app
from match.models import Match, MatchPlayer
from game_event.models import Event, MatchSubstitution
from player.models import Player
8

available_competitions = [
    # 2000,2001,
    2002,2003,2013,2014,2015,2016,2017,2018,2019,2021
]

@database_population_api.route('/match-event')
class PopulateMatchesEvents(Resource):
    @database_empty_required(Match)
    @database_empty_required(Event)
    def get(self):
        """population order : 4"""
        all_players = Player.query.all()
        all_players_id = [player.id for player in all_players]
        done_competitions = 1
        for competition in available_competitions:
            url = 'https://data-ui.football-data.org/fd/competitions/%s/matches' % competition
            headers ={}
            headers['X-Auth-Token'] =  current_app.config['SOURCE_API_SECRET_KEY']
            resp = requests.get(url,headers=headers)
            matches = resp.json()['data']

            for match in matches:
                #if the attrs are null skip it
                if len(match['homeTeam']['lineup']) == 0:
                    continue
                if match['homeTeam']['captain']['id'] not in all_players_id or match['awayTeam']['captain']['id'] not in all_players_id or match['status'] == 'POSTPONED':
                    continue
                match_to_insert = Match(
                    id = match['id'],
                    competition_id = match['competition']['id'],
                    utcDate = match['utcDate'],
                    status = match['status'],
                    homeTeam = match['homeTeam']['id'],
                    awayTeam = match['awayTeam']['id'],
                    lastUpdated = match['lastUpdated'],
                    homeTeamCaptain = match['homeTeam']['captain']['id'],
                    awayTeamCaptain = match['awayTeam']['captain']['id'],
                )
                db.session.add(match_to_insert)
                db.session.commit()

                for match_player in match['homeTeam']['lineup']:
                    if match_player['id'] in all_players_id:
                        match_player_to_insert = MatchPlayer(
                            player_id = match_player['id'],
                            match_id = match['id'],
                            playerPlayingStatus = 'LN'
                        )
                        db.session.add(match_player_to_insert)
                for match_player in match['homeTeam']['bench']:
                    if match_player['id'] in all_players_id:
                        match_player_to_insert = MatchPlayer(
                            player_id = match_player['id'],
                            match_id = match['id'],
                            playerPlayingStatus = 'BN'
                        )
                        db.session.add(match_player_to_insert)

                for match_player in match['awayTeam']['lineup']:
                    if match_player['id'] in all_players_id:
                        match_player_to_insert = MatchPlayer(
                            player_id = match_player['id'],
                            match_id = match['id'],
                            playerPlayingStatus = 'LN'
                        )
                        db.session.add(match_player_to_insert)
                for match_player in match['awayTeam']['bench']:
                    if match_player['id'] in all_players_id:
                        match_player_to_insert = MatchPlayer(
                            player_id = match_player['id'],
                            match_id = match['id'],
                            playerPlayingStatus = 'BN'
                        )
                        db.session.add(match_player_to_insert)
                for goal in match.get('goals'):
                    if goal['scorer']['id'] in all_players_id:
                        event_to_insert = Event(
                            minute = goal['minute'],
                            player_id = goal['scorer']['id'],
                            event_type = "GO",
                            match_id = match['id']
                        )
                        db.session.add(event_to_insert)
                    if goal.get('assist') != None:
                        if goal['assist']['id'] in all_players_id:
                            event_to_insert = Event(
                                minute = goal['minute'],
                                player_id = goal['assist']['id'],
                                event_type = "AS",
                                match_id = match['id']
                            )
                            db.session.add(event_to_insert)
                
                for card in match.get('bookings'):
                    if card['player']['id'] in all_players_id:
                        event_to_insert = Event(
                            minute = card['minute'],
                            player_id = card['player']['id'],
                            event_type = card['card'],
                            match_id = match['id']
                        )
                        db.session.add(event_to_insert)
                for substitution in match.get('substitutions'):
                    if substitution['playerIn']['id'] in all_players_id and substitution['playerOut']['id'] in all_players_id:
                        event_to_insert = MatchSubstitution(
                            minute = substitution['minute'],
                            player_in_id = substitution['playerIn']['id'],
                            player_out_id = substitution['playerOut']['id'],
                            match_id = match['id']
                        )
                        db.session.add(event_to_insert)

                db.session.commit()
            print("remaining competitions: %s" % (len(available_competitions)-done_competitions))
            done_competitions+=1
                