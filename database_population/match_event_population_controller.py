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
    def get_match_substitutions(match):
        subs = []
        for substitution in match.get('substitutions'):
            sub_to_insert = MatchSubstitution(
                minute=substitution.get('minute'),
                player_in_id=substitution.get('playerIn').get('id'),
                player_out_id=substitution.get('playerOut').get('id'),
                match_id=match.get('id')
            )
            subs.append(sub_to_insert)
        return subs
    @staticmethod
    def get_match_events(match):
        events = []
        for goal in match.get('goals'):
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
                event_to_insert = Event(
                    minute=goal['minute'],
                    player_id=goal['assist']['id'],
                    event_type="AS",
                    match_id=match['id']
                )
                events.append(event_to_insert)

        for card in match.get('bookings'):
            event_to_insert = Event(
                minute=card['minute'],
                player_id=card['player']['id'],
                event_type=card['card'],
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
                    home_away="HOME",
                    minutes_played = 0,
                    player_score = 0

                )
                players.append(match_player_to_insert)
        for match_player in match['homeTeam']['bench']:
            if match_player['id'] in all_players_id:
                match_player_to_insert = MatchPlayer(
                    player_id=match_player['id'],
                    match_id=match['id'],
                    playerPlayingStatus='BN',
                    lastUpdated=match['lastUpdated'],
                    home_away="HOME",
                    minutes_played = 0,
                    player_score = 0
                )
                players.append(match_player_to_insert)

        for match_player in match['awayTeam']['lineup']:
            if match_player['id'] in all_players_id:
                match_player_to_insert = MatchPlayer(
                    player_id=match_player['id'],
                    match_id=match['id'],
                    playerPlayingStatus='LN',
                    lastUpdated=match['lastUpdated'],
                    home_away="AWAY",
                    minutes_played = 0,
                    player_score = 0
                )
                players.append(match_player_to_insert)
        for match_player in match['awayTeam']['bench']:
            if match_player['id'] in all_players_id:
                match_player_to_insert = MatchPlayer(
                    player_id=match_player['id'],
                    match_id=match['id'],
                    playerPlayingStatus='BN',
                    lastUpdated=match['lastUpdated'],
                    home_away="AWAY",
                    minutes_played = 0,
                    player_score = 0
                )
                players.append(match_player_to_insert)
        return players
    @staticmethod
    def insert_match_event(match):
        # all_players_id = [player.id for player in Player.query.all()]
        all_players = Player.query
        
        match_to_insert = Match(
            id=match['id'],
            competition_id=match.get('competition').get('id'),
            utcDate=match.get('utcDate'),
            status=match.get('status'),
            homeTeam_id=match.get('homeTeam').get('id'),
            awayTeam_id=match.get('awayTeam').get('id'),
            homeTeamScore=match.get('score').get('fullTime').get('homeTeam'),
            awayTeamScore=match.get('score').get('fullTime').get('awayTeam'),
            lastUpdated=match.get('lastUpdated'),
            homeTeamCaptain_id=match.get('homeTeam').get('captain').get('id'),
            awayTeamCaptain_id=match.get('awayTeam').get('captain').get('id'),
        )
        db.session.add(match_to_insert)
        subs = PopulateMatchesEvents.get_match_substitutions(match)
        events = PopulateMatchesEvents.get_match_events(match)
        players = PopulateMatchesEvents.get_match_players(match)
        for event in events:
            if all_players.filter(Player.id == event.player_id).first():
                db.session.add(event)
        for sub in subs:
            if all_players.filter(Player.id == sub.player_out_id).first() and all_players.filter(Player.id == sub.player_in_id).first():
                db.session.add(sub)
        for player in players:
            if all_players.filter(Player.id == player.player_id).first():
                db.session.add(player)
        db.session.commit()
        

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
            resp = requests.get(url, headers=headers, verify = False)
            matches = resp.json()['data']

            for match in matches:
                # if match.get('status') == 'SCHEDULED':

                # if len(match['homeTeam']['lineup']) == 0:
                #     continue

                if match.get('status')!="SCHEDULED" and (match.get('homeTeam').get('captain').get('id') not in all_players_id or match.get('awayTeam').get('captain').get('id') not in all_players_id or match['status'] == 'POSTPONED'):
                    continue

                PopulateMatchesEvents.insert_match_event(match)

            print("remaining competitions: %s" %
                  (len(available_competitions)-done_competitions))
            done_competitions += 1
