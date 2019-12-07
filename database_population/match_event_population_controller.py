import requests
from flask_restplus import Resource
from .api_model import database_population_update_api
from .database_decorators import database_empty_required
from config import db
from flask import current_app
from match.models import Match, MatchPlayer
from game_event.models import Event, MatchSubstitution
from player.models import Player
from .globals import available_competitions, football_api


@database_population_update_api.route('/match-event-populate')
class PopulateMatchesEvents(Resource):

    @staticmethod
    def get_match_events(match):
        all_players_id = [player.id for player in Player.query.all()]
        events = []
        for goal in match.get('goals'):
            if goal['scorer']['id'] in all_players_id:
                if goal['type'] == "OWN":
                    event_to_insert = Event(
                        minute=goal['minute'],
                        player_id=goal['scorer']['id'],
                        event_type="OWNGO",
                        match_id=match['id']
                    )
                else:
                    event_to_insert = Event(
                        minute=goal['minute'],
                        player_id=goal['scorer']['id'],
                        event_type="GO",
                        match_id=match['id']
                    )
                events.append(event_to_insert)
            if goal.get('assist') != None:
                if goal['assist']['id'] in all_players_id:
                    event_to_insert = Event(
                        minute=goal['minute'],
                        player_id=goal['assist']['id'],
                        event_type="AS",
                        match_id=match['id']
                    )
                    events.append(event_to_insert)

        for card in match.get('bookings'):
            if card['player']['id'] in all_players_id:
                event_to_insert = Event(
                    minute=card['minute'],
                    player_id=card['player']['id'],
                    event_type=card['card'],
                    match_id=match['id']
                )
                events.append(event_to_insert)
        for substitution in match.get('substitutions'):
            if substitution['playerIn']['id'] in all_players_id and substitution['playerOut']['id'] in all_players_id:
                event_to_insert = MatchSubstitution(
                    minute=substitution['minute'],
                    player_in_id=substitution['playerIn']['id'],
                    player_out_id=substitution['playerOut']['id'],
                    match_id=match['id']
                )
                events.append(event_to_insert)
        return events

    @staticmethod
    def get_match_players(match):
        all_players_id = [player.id for player in Player.query.all()]
        players = []
        for match_player in match['homeTeam']['lineup']:
            if match_player['id'] in all_players_id:
                match_player_to_insert = MatchPlayer(
                    player_id=match_player['id'],
                    match_id=match['id'],
                    playerPlayingStatus='LN',
                    lastUpdated=match['lastUpdated'],
                    home_away="HOME"
                )
                players.append(match_player_to_insert)
        for match_player in match['homeTeam']['bench']:
            if match_player['id'] in all_players_id:
                match_player_to_insert = MatchPlayer(
                    player_id=match_player['id'],
                    match_id=match['id'],
                    playerPlayingStatus='BN',
                    lastUpdated=match['lastUpdated'],
                    home_away="HOME"
                )
                players.append(match_player_to_insert)

        for match_player in match['awayTeam']['lineup']:
            if match_player['id'] in all_players_id:
                match_player_to_insert = MatchPlayer(
                    player_id=match_player['id'],
                    match_id=match['id'],
                    playerPlayingStatus='LN',
                    lastUpdated=match['lastUpdated'],
                    home_away="AWAY"
                )
                players.append(match_player_to_insert)
        for match_player in match['awayTeam']['bench']:
            if match_player['id'] in all_players_id:
                match_player_to_insert = MatchPlayer(
                    player_id=match_player['id'],
                    match_id=match['id'],
                    playerPlayingStatus='BN',
                    lastUpdated=match['lastUpdated'],
                    home_away="AWAY"
                )
                players.append(match_player_to_insert)
        return players
    @staticmethod
    def insert_match_event(match):
        match_to_insert = Match(
            id=match['id'],
            competition_id=match['competition']['id'],
            utcDate=match['utcDate'],
            status=match['status'],
            homeTeam=match['homeTeam']['id'],
            awayTeam=match['awayTeam']['id'],
            homeTeamScore=match.get('score').get('fullTime').get('homeTeam'),
            awayTeamScore=match.get('score').get('fullTime').get('awayTeam'),
            lastUpdated=match['lastUpdated'],
            homeTeamCaptain=match['homeTeam']['captain']['id'],
            awayTeamCaptain=match['awayTeam']['captain']['id'],
        )
        db.session.add(match_to_insert)
        events = PopulateMatchesEvents.get_match_events(match)
        players = PopulateMatchesEvents.get_match_players(match)
        for event in events:
            db.session.add(event)
        for player in players:
            db.session.add(player)
        db.session.commit()
        return
        

    @database_empty_required(Match)
    @database_empty_required(Event)
    def get(self):
        """population order : 4"""
        all_players_id = [player.id for player in Player.query.all()]
        done_competitions = 1
        for competition in available_competitions:
            url = football_api['MatchEvent'] % competition
            headers = {}
            headers['X-Auth-Token'] = current_app.config['SOURCE_API_SECRET_KEY']
            resp = requests.get(url, headers=headers)
            matches = resp.json()['data']

            for match in matches:
                if len(match['homeTeam']['lineup']) == 0:
                    continue
                if match['homeTeam']['captain']['id'] not in all_players_id or match['awayTeam']['captain']['id'] not in all_players_id or match['status'] == 'POSTPONED':
                    continue
                PopulateMatchesEvents.insert_match_event(match)

            print("remaining competitions: %s" %
                  (len(available_competitions)-done_competitions))
            done_competitions += 1
